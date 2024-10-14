
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from subject.views import SubjectViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)

urlpatterns = router.urls