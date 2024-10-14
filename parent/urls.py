from parent.views import ParentViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include


router = DefaultRouter()
router.register(r'parents', ParentViewSet, basename='parents')

urlpatterns = [
    path('', include(router.urls)),]