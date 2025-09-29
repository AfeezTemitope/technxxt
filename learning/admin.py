# learning/admin.py
from django.contrib import admin
from .models import Course, Module, Lesson, Exam, Question, UserLessonProgress, ExamResult


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('title',)}

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class ModuleAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ['title', 'course', 'order']

admin.site.register(Module, ModuleAdmin)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['module', 'passing_score']

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'text']
    inlines = []

# Progress models (optional)
admin.site.register([UserLessonProgress, ExamResult])