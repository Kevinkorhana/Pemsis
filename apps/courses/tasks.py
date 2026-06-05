import csv
import datetime
from celery import shared_task
from django.contrib.auth.models import User
from .models import Course, Enrollment

# Task 1: Asynchronous Email Sending
@shared_task
def send_enrollment_email(student_email, course_title):
    print("--- [CELERY WORKER] MEMICU TASK EMAIL ---")
    return f"Notifikasi email sukses dikirim ke {student_email} untuk kelas {course_title}"

# Task 2: Asynchronous Certificate Generation
@shared_task
def generate_certificate(student_name, course_title):
    print("--- [CELERY WORKER] PROSES GENERATE SERTIFIKAT ---")
    return f"Sertifikat kelulusan kelas '{course_title}' atas nama {student_name} sukses dibuat."

# Task 3: Scheduled Task - Update Course Statistics (Beat)
@shared_task
def update_course_statistics():
    print("--- [CELERY BEAT] SEEDING STATISTIK KURSUS ---")
    courses = Course.objects.all()
    for course in courses:
        enrollment_count = Enrollment.objects.filter(course=course).count()
        print(f"Kursus '{course.title}': Total {enrollment_count} siswa aktif.")
    return "Statistik pendaftaran seluruh kelas diperbarui."

# Task 4: Asynchronous Export Report
@shared_task
def export_course_report():
    print("--- [CELERY WORKER] MEMPROSES EXPORT DATA CSV ---")
    file_path = f"media/reports/course_report_{datetime.date.today()}.csv"
    
    courses = Course.objects.all()
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID Kursus', 'Judul Kelas', 'Instruktur'])
        for course in courses:
            writer.writerow([course.id, course.title, course.instructor.username])
            
    return f"Laporan CSV berhasil diekspor ke {file_path}"