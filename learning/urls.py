from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet, basename='course')

router.register(r'progress', views.ProgressViewSet, basename='progress')
router.register(r'exams', views.ExamViewSet, basename='exam')

urlpatterns = [
    path('', include(router.urls)),
]