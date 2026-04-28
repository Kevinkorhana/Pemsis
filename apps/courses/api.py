from ninja import Router, Schema
from typing import List
from .models import Course
from apps.authentication.jwt import AuthBearer
from apps.authentication.permissions import is_instructor
from ninja.errors import HttpError

router = Router(tags=["Courses"])

class CourseSchema(Schema):
    id: int = None
    title: str
    description: str
    price: float = None

# PUBLIC: List Courses
@router.get("/", response=List[CourseSchema])
def list_courses(request, limit: int = 10, offset: int = 0):
    return Course.objects.all()[offset:offset+limit]

# PROTECTED: Create Course (Instructor Only)
@router.post("/", auth=AuthBearer())
@is_instructor
def create_course(request, data: CourseSchema):
    course = Course.objects.create(
        **data.dict(),
        instructor=request.auth
    )
    return {"id": course.id, "title": course.title}

# PROTECTED: Delete Course (Ownership Check)
@router.delete("/{course_id}", auth=AuthBearer())
def delete_course(request, course_id: int):
    # Gunakan filter agar tidak error jika ID tidak ada
    course = Course.objects.filter(id=course_id).first()
    if not course:
        raise HttpError(404, "Kursus tidak ditemukan.")
        
    # Pengecekan Ownership & Role
    if course.instructor != request.auth and request.auth.profile.role != 'admin':
        raise HttpError(403, "Anda tidak memiliki izin untuk menghapus kursus ini.")
        
    course.delete()
    return {"success": True}
    # Tambahkan ke apps/courses/api.py

class EnrollmentSchema(Schema):
    course_id: int

@router.post("/enrollments", auth=AuthBearer())
def enroll_to_course(request, data: EnrollmentSchema):
    # Cek apakah sudah terdaftar
    from .models import Enrollment
    enroll, created = Enrollment.objects.get_or_create(
        student=request.auth,
        course_id=data.course_id
    )
    if not created:
        return {"message": "Sudah terdaftar di kursus ini"}
    return {"message": "Pendaftaran berhasil"}

@router.get("/enrollments/my-courses", auth=AuthBearer())
def my_courses(request):
    from .models import Enrollment
    # Menggunakan manager for_student_dashboard yang Anda buat di models.py
    enrollments = Enrollment.objects.filter(student=request.auth).for_student_dashboard()
    return [
        {
            "id": e.id,
            "course_title": e.course.title,
            "enrolled_at": e.enrolled_at
        } for e in enrollments
    ]

@router.post("/enrollments/{lesson_id}/progress", auth=AuthBearer())
def mark_lesson_complete(request, lesson_id: int):
    from .models import Progress
    progress, created = Progress.objects.update_or_create(
        student=request.auth,
        lesson_id=lesson_id,
        defaults={'completed': True}
    )
    return {"status": "Lesson completed"}

@router.get("/{course_id}", response=CourseSchema)
def get_course_detail(request, course_id: int):
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Course, id=course_id)

# Endpoint Update Kursus (Hanya Owner/Instructor)
@router.patch("/{course_id}", auth=AuthBearer())
@is_instructor
def update_course(request, course_id: int, data: CourseSchema):
    course = Course.objects.filter(id=course_id, instructor=request.auth).first()
    if not course:
        raise HttpError(404, "Kursus tidak ditemukan atau Anda bukan pemiliknya")
    
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(course, attr, value)
    course.save()
    return {"message": "Course updated successfully"}