from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog.api.views import BlogViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'blogs', BlogViewSet, basename='blog')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
