from django.contrib import admin
from .models import (
    Course,
    Lesson,
    Category,
    Enrollment,
    Progress,
    Profile
)


# ========================
# LESSON INLINE
# ========================
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ('order',)


# ========================
# COURSE ADMIN
# ========================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'created_at')
    search_fields = ('title', 'instructor__username')
    list_filter = ('category', 'created_at')
    list_select_related = ('instructor', 'category')  # optimization 🔥
    ordering = ('-created_at',)
    inlines = [LessonInline]


# ========================
# CATEGORY ADMIN
# ========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)
    ordering = ('name',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    ordering = ('order',)


# ========================
# ENROLLMENT ADMIN
# ========================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    search_fields = ('student__username', 'course__title')
    list_filter = ('course', 'enrolled_at')
    list_select_related = ('student', 'course')  # optimization 🔥
    ordering = ('-enrolled_at',)


# ========================
# PROGRESS ADMIN
# ========================
@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed')
    search_fields = ('student__username', 'lesson__title')
    list_filter = ('completed',)
    list_select_related = ('student', 'lesson')  # optimization 🔥


# ========================
# PROFILE ADMIN
# ========================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username',)
    list_filter = ('role',)
    list_select_related = ('user',)  # optimization 🔥


