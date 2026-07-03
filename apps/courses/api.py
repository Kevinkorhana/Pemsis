from ninja import Router, Schema, Query
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Q
from django_ratelimit.decorators import ratelimit
from ninja.errors import HttpError
import json

# Import bawaan dari proyek Anda
from .models import Course, Enrollment, Progress
from apps.authentication.jwt import AuthBearer
from apps.authentication.permissions import is_instructor

# Import Celery & MongoDB dari Progress 4
from .tasks import send_enrollment_email, generate_certificate, export_course_report
from core.mongodb import mongo_logger 

router = Router(tags=["Courses"])

# ==========================================
# SCHEMA DEFINITIONS
# ==========================================
class CourseSchema(Schema):
    id: int = None
    title: str
    description: str
    price: float = None

class EnrollmentSchema(Schema):
    course_id: int

# Schema Baru untuk Filtering, Search, & Sorting (Diperbaiki: Tanpa field level)
class CourseFilterSchema(Schema):
    search: Optional[str] = None
    sort_by: Optional[str] = "newest"  # Pilihan: newest, title

# ==========================================
# HELPER: CACHE INVALIDATION STRATEGY
# ==========================================
def clear_course_cache(course_id=None):
    """Menghapus cache di Redis saat data berubah agar tidak basi (Invalidation Strategy)"""
    # Karena kita menggunakan pagination dinamis, kita bersihkan cache berbasis pola atau cache utama
    cache.delete_pattern("all_courses_cache_*") if hasattr(cache, "delete_pattern") else cache.clear()
    if course_id:
        cache.delete(f"course_detail_{course_id}")


# ========================================================
# KELOMPOK 1: ENDPOINT DENGAN PATH STATIS (POSISI ATAS)
# ========================================================

# GET: List Courses (Redis Cached, Paginated, Filtered, & Rate Limited)
@router.get("/", response=List[CourseSchema])
@ratelimit(key='ip', rate='60/m', block=True)
def list_courses(request, filters: CourseFilterSchema = Query(...), limit: int = 10, offset: int = 0):
    # Buat cache_key dinamis berdasarkan filter (tanpa level), offset, dan limit pagination
    cache_key = f"all_courses_cache_search_{filters.search}_sort_{filters.sort_by}_offset_{offset}_limit_{limit}"
    cached_courses = cache.get(cache_key)
    
    if cached_courses:
        return json.loads(cached_courses) if isinstance(cached_courses, str) else cached_courses
        
    # Ambil queryset dasar dari PostgreSQL
    queryset = Course.objects.all()
    
    # Fitur Tambahan: Pencarian Lanjutan (Search)
    if filters.search:
        queryset = queryset.filter(
            Q(title__icontains=filters.search) | Q(description__icontains=filters.search)
        )
        
    # Fitur Tambahan: Pengurutan (Sorting)
    if filters.sort_by == "title":
        queryset = queryset.order_by("title")
    else:
        queryset = queryset.order_by("-id")  # Default: Newest berdasarkan ID
        
    # Terapkan Pagination
    paginated_queryset = list(queryset[offset:offset+limit])
    
    # Simpan ke Redis cache selama 15 menit
    cache.set(cache_key, paginated_queryset, timeout=60*15)
    return paginated_queryset


# POST: Export Report (Celery Async CSV Export)
@router.post("/export-report", auth=AuthBearer())
def trigger_report_export(request):
    task = export_course_report.delay()
    return {
        "message": "Proses ekspor laporan CSV sedang berjalan di background worker.",
        "task_id": task.id
    }


# POST: Enroll to Course (Celery Async Email & MongoDB Log)
@router.post("/enrollments", auth=AuthBearer())
def enroll_to_course(request, data: EnrollmentSchema):
    enroll, created = Enrollment.objects.get_or_create(
        student=request.auth,
        course_id=data.course_id
    )
    if not created:
        return {"message": "Sudah terdaftar di kursus ini"}
        
    # 1. MongoDB Integration: Catat aktivitas enroll student
    mongo_logger.log_activity(
        user_id=request.auth.id,
        username=request.auth.username,
        activity_type="ENROLL_COURSE",
        details={"course_id": data.course_id, "course_title": enroll.course.title}
    )
    
    # 2. Celery Task Integration: Kirim email asinkronus (Async Notification)
    send_enrollment_email.delay(request.auth.email, enroll.course.title)
    
    return {"message": "Pendaftaran berhasil"}


# GET: My Courses Dashboard
@router.get("/enrollments/my-courses", auth=AuthBearer())
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.auth)
    return [
        {
            "id": e.id,
            "course_title": e.course.title,
            "enrolled_at": e.enrolled_at
        } for e in enrollments
    ]


# POST: Mark Lesson Complete (Celery Async Certificate Trigger)
@router.post("/enrollments/{lesson_id}/progress", auth=AuthBearer())
def mark_lesson_complete(request, lesson_id: int):
    progress, created = Progress.objects.update_or_create(
        student=request.auth,
        lesson_id=lesson_id,
        defaults={'completed': True}
    )
    
    # Celery Task Integration: Pemicu pembuatan sertifikat asinkronus
    generate_certificate.delay(request.auth.username, "Kursus Pilihan LMS")
    
    return {"status": "Lesson completed"}


# POST: Create Course (Instructor Only + Invalidation)
@router.post("/", auth=AuthBearer())
@is_instructor
def create_course(request, data: CourseSchema):
    course = Course.objects.create(
        **data.dict(),
        instructor=request.auth
    )
    
    # Cache Invalidation: Bersihkan cache list karena ada kelas baru
    clear_course_cache()
    return {"id": course.id, "title": course.title}


# ========================================================
# KELOMPOK 2: ENDPOINT DENGAN PATH DINAMIS / ID (POSISI BAWAH)
# ========================================================

# GET: Course Detail (Redis Cached & MongoDB Activity Log)
# GET: Course Detail (Redis Cached & MongoDB Activity Log)
@router.get("/{course_id}", response=CourseSchema)
@ratelimit(key='ip', rate='60/m', block=True)
def get_course_detail(request, course_id: int):
    cache_key = f"course_detail_{course_id}"
    cached_course = cache.get(cache_key)
    
    # Ambil object dari Postgres jika cache kosong (Cache Miss)
    if not cached_course:
        cached_course = get_object_or_404(Course, id=course_id)
        cache.set(cache_key, cached_course, timeout=60*15)
    
    # FIX: Gunakan hasattr() untuk mengecek apakah request memiliki atribut 'auth'
    # Ini mencegah AttributeError ketika diakses oleh user anonim/belum login
    user_auth = request.auth if hasattr(request, 'auth') else None
    
    # MongoDB Integration: Catat log siswa yang melihat detail kelas (Hanya jika login)
    if user_auth:
        mongo_logger.log_activity(
            user_id=user_auth.id,
            username=user_auth.username,
            activity_type="VIEW_COURSE",
            details={"course_id": course_id, "course_title": cached_course.title}
        )
        
    return cached_course

# PATCH: Update Course (Instructor Owner + Invalidation)
@router.patch("/{course_id}", auth=AuthBearer())
@is_instructor
def update_course(request, course_id: int, data: CourseSchema):
    course = Course.objects.filter(id=course_id, instructor=request.auth).first()
    if not course:
        raise HttpError(404, "Kursus tidak ditemukan atau Anda bukan pemiliknya")
    
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(course, attr, value)
    course.save()
    
    # Cache Invalidation: Hapus cache list dan detail kelas ini yang lama
    clear_course_cache(course_id)
    return {"message": "Course updated successfully"}


# DELETE: Delete Course (Ownership Check + Invalidation)
@router.delete("/{course_id}", auth=AuthBearer())
def delete_course(request, course_id: int):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        raise HttpError(404, "Kursus tidak ditemukan.")
        
    if course.instructor != request.auth and request.auth.profile.role != 'admin':
        raise HttpError(403, "Anda tidak memiliki izin untuk menghapus kursus ini.")
        
    course.delete()
    
    # Cache Invalidation: Bersihkan dari memori Redis
    clear_course_cache(course_id)
    return {"success": True}