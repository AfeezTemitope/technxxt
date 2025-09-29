from rest_framework import serializers
from django.utils import timezone
from .models import (
    Course, Module, Lesson, Exam, Question,
    UserLessonProgress, ExamResult
)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d']


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'passing_score', 'questions']


class LessonSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order', 'completed']

    def get_completed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return UserLessonProgress.objects.filter(
            user=user, lesson=obj, completed=True
        ).exists()


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    has_exam = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'lessons', 'has_exam']

    def get_has_exam(self, obj):
        return hasattr(obj, 'exam')


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'modules']


class UserLessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLessonProgress
        fields = ['lesson', 'completed']
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        lesson = data['lesson']
        if not lesson.module.course.is_active:
            raise serializers.ValidationError("Cannot complete lessons in inactive courses.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        progress, created = UserLessonProgress.objects.update_or_create(
            user=user,
            lesson=validated_data['lesson'],
            defaults={
                'completed': validated_data['completed'],
                'completed_at': timezone.now() if validated_data['completed'] else None
            }
        )
        return progress


class SubmitExamSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.CharField(max_length=1)
    )

    def validate_answers(self, value):
        exam = self.context['exam']
        question_ids = set(str(q.id) for q in exam.questions.all())
        provided_ids = set(value.keys())

        if provided_ids != question_ids:
            raise serializers.ValidationError("Answers must be provided for all questions.")
        for ans in value.values():
            if ans not in ['A', 'B', 'C', 'D']:
                raise serializers.ValidationError("Invalid answer option.")
        return value

    def save(self):
        user = self.context['request'].user
        exam = self.context['exam']
        answers = self.validated_data['answers']

        correct = 0
        total = exam.questions.count()

        for q in exam.questions.all():
            if answers.get(str(q.id)) == q.correct_option:
                correct += 1

        score = (correct / total) * 100
        passed = score >= exam.passing_score

        result, created = ExamResult.objects.update_or_create(
            user=user,
            exam=exam,
            defaults={'score': score, 'passed': passed}
        )
        return result