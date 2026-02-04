from django.urls import path, include
from rest_framework.routers import DefaultRouter

from donation.api.views import (
    DonationViewSet,
    DonationTargetViewSet,
    DonationStatsView
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'donations', DonationViewSet, basename='donation')
router.register(r'targets', DonationTargetViewSet, basename='donation-target')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('stats/', DonationStatsView.as_view(), name='donation-stats'),
]
