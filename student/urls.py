from rest_framework.routers import DefaultRouter
from django.urls import path, include

from student.views import StudentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='teachers')

urlpatterns = [
    path('', include(router.urls)),]