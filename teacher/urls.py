from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import  TeacherSectionSubjectView, TeacherViewSet

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teachers')
# router.register(r'teacher-section-subject', TeacherSectionSubjectViewSet, basename='teacher_section')  # Updated path

urlpatterns = [
    path('', include(router.urls)),
    path('assign-teacher/', TeacherSectionSubjectView.as_view(), name='assign-teacher'),
    path('assign-teacher/<int:pk>/', TeacherSectionSubjectView.as_view(), name='crud-assignment'),  # GET, PUT, PATCH, DELETE by ID
]
