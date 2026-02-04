"""
URL configuration for Network app API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from network.api.views import FollowViewSet, ReportViewSet

router = SimpleRouter()
router.register('api/network', FollowViewSet, basename='follow')
router.register('api/network/reports', ReportViewSet, basename='report')

urlpatterns = router.urls
