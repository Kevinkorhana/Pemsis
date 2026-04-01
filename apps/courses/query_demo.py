from django.db import connection
from courses.models import Course


def run_demo():
    print("=== TANPA OPTIMIZATION (N+1) ===")
    connection.queries_log.clear()

    courses = Course.objects.all()
    for course in courses:
        print(course.title, "-", course.instructor.username)

    print("Jumlah Query:", len(connection.queries))


    print("\n=== DENGAN OPTIMIZATION ===")
    connection.queries_log.clear()

    courses = Course.objects.select_related('instructor')
    for course in courses:
        print(course.title, "-", course.instructor.username)

    print("Jumlah Query:", len(connection.queries))