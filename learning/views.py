from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.db import transaction
from .models import Course, Exam, UserLessonProgress, ExamResult
from .serializers import (
    CourseSerializer, UserLessonProgressSerializer,
    SubmitExamSerializer, ExamSerializer
)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List active courses with full module/lesson tree.
    Cached for 15 minutes per user.
    """
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(is_active=True).prefetch_related(
            'modules__lessons',
            'modules__exam__questions'
        ).order_by('id')

    @method_decorator(cache_page(60 * 15))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProgressViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def mark_lesson_complete(self, request):
        serializer = UserLessonProgressSerializer(
            data={'lesson': request.data.get('lesson_id'), 'completed': True},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExamViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def active_list(self, request):
        """List exams from active courses only"""
        exams = Exam.objects.select_related(
            'module__course'
        ).filter(
            module__course__is_active=True
        ).order_by('module__course__title')
        data = [
            {
                'id': exam.id,
                'course_title': exam.module.course.title,
                'module_title': exam.module.title,
            }
            for exam in exams
        ]
        return Response(data)

    @action(detail=True, methods=['get'])
    def start(self, request, pk=None):
        try:
            exam = Exam.objects.select_related(
                'module__course'
            ).prefetch_related('questions').get(pk=pk)
            if not exam.module.course.is_active:
                return Response(
                    {"error": "Exam not available"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = ExamSerializer(exam)
            return Response(serializer.data)
        except Exam.DoesNotExist:
            return Response(
                {"error": "Exam not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def submit(self, request, pk=None):
        try:
            exam = Exam.objects.get(pk=pk)
            if not exam.module.course.is_active:
                return Response(
                    {"error": "Exam not available"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except Exam.DoesNotExist:
            return Response(
                {"error": "Exam not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SubmitExamSerializer(
            data=request.data,
            context={'exam': exam, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({
            'score': result.score,
            'passed': result.passed,
            'message': 'Exam submitted successfully!'
        }, status=status.HTTP_201_CREATED)