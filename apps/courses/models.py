from django.db import models
from django.contrib.auth.models import User


# ========================
# PROFILE (ROLE USER)
# ========================
class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ========================
# CATEGORY (HIERARCHY)
# ========================
class Category(models.Model):
    name = models.CharField(max_length=255)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        return self.name


# ========================
# COURSE QUERYSET (OPTIMIZATION)
# ========================
class CourseQuerySet(models.QuerySet):
    def for_listing(self):
        return self.select_related('instructor', 'category') \
                   .prefetch_related('lessons')


class CourseManager(models.Manager):
    def get_queryset(self):
        return CourseQuerySet(self.model, using=self._db)

    def for_listing(self):
        return self.get_queryset().for_listing()


# ========================
# COURSE
# ========================
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()

    def __str__(self):
        return self.title


# ========================
# LESSON
# ========================
class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.course.title})"


# ========================
# ENROLLMENT QUERYSET
# ========================
class EnrollmentQuerySet(models.QuerySet):
    def for_student_dashboard(self):
        return self.select_related('course') \
                   .prefetch_related('course__lessons')


class EnrollmentManager(models.Manager):
    def get_queryset(self):
        return EnrollmentQuerySet(self.model, using=self._db)

    def for_student_dashboard(self):
        return self.get_queryset().for_student_dashboard()


# ========================
# ENROLLMENT
# ========================
class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    objects = EnrollmentManager()

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


# ========================
# PROGRESS
# ========================
class Progress(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress'
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress'
    )

    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"