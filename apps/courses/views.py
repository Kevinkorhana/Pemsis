from django.http import JsonResponse
from django.db.models import Count, Avg, Max, Min
from .models import Course, Enrollment

# =========================
# 1. COURSE LIST
# =========================

def course_list_baseline(request):
    courses = Course.objects.all()
    data = []

    for c in courses:
        data.append({
            'course': c.title,
            'teacher': c.instructor.username,
        })

    return JsonResponse({'data': data})


def course_list_optimized(request):
    courses = Course.objects.select_related('instructor').all()
    data = []

    for c in courses:
        data.append({
            'course': c.title,
            'teacher': c.instructor.username,
        })

    return JsonResponse({'data': data})


# =========================
# 2. COURSE MEMBERS
# =========================

def course_members_baseline(request):
    courses = Course.objects.all()
    data = []

    for c in courses:
        member_count = Enrollment.objects.filter(course=c).count()

        data.append({
            'course': c.title,
            'member_count': member_count,
        })

    return JsonResponse({'data': data})


def course_members_optimized(request):
    courses = Course.objects.annotate(
        member_count=Count('enrollments')  
    )

    data = []

    for c in courses:
        data.append({
            'course': c.title,
            'member_count': c.member_count,
        })

    return JsonResponse({'data': data})

# =========================
# 3. COURSE DASHBOARD
# =========================

def course_dashboard_baseline(request):
    courses = Course.objects.all()

    total = courses.count()

    prices = []
    for c in courses:
        if c.price:
            prices.append(c.price)

    max_price = max(prices) if prices else 0
    min_price = min(prices) if prices else 0
    avg_price = sum(prices) / len(prices) if prices else 0

    return JsonResponse({
        'total': total,
        'max_price': max_price,
        'min_price': min_price,
        'avg_price': avg_price,
    })


def course_dashboard_optimized(request):
    stats = Course.objects.aggregate(
        total=Count('id'),
        max_price=Max('price'),
        min_price=Min('price'),
        avg_price=Avg('price'),
    )

    return JsonResponse(stats)