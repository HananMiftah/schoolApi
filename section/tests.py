# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from section.views import SectionViewSet

router = DefaultRouter()
router.register(r'section', SectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
