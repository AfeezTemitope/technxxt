from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Course(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField()
    is_active = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'slug']),
        ]

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        db_index=True
    )
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(db_index=True)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        db_index=True
    )
    title = models.CharField(max_length=100)
    content = models.TextField()  # For MVP; extend later for media
    order = models.PositiveIntegerField(db_index=True)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['module', 'order']),
        ]

    def __str__(self):
        return self.title


class Exam(models.Model):
    module = models.OneToOneField(
        Module,
        on_delete=models.CASCADE,
        related_name='exam'
    )
    passing_score = models.FloatField(default=70.0)

    def __str__(self):
        return f"Exam for {self.module.title}"


class Question(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        db_index=True
    )
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1)  # 'A', 'B', 'C', 'D'

    def __str__(self):
        return self.text[:50]


class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, db_index=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')
        indexes = [
            models.Index(fields=['user', 'lesson']),
            models.Index(fields=['user', 'completed']),
        ]

    def save(self, *args, **kwargs):
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.lesson} - {'✅' if self.completed else '⏳'}"


class ExamResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, db_index=True)
    score = models.FloatField()
    passed = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'exam')
        indexes = [
            models.Index(fields=['user', 'exam']),
            models.Index(fields=['user', 'passed']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.exam} - {self.score}%"