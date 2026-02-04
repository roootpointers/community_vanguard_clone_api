from rest_framework.routers import SimpleRouter
from exchange.api.views import (
    ExchangeViewSet,
    CategoryViewSet,
    SubCategoryViewSet,
    BusinessHoursViewSet,
    TimeSlotViewSet,
    BookingViewSet
)
from exchange.api.views.review import ExchangeReviewViewSet
from exchange.api.views.quote import ExchangeQuoteViewSet
from exchange.api.views.admin import AdminExchangeViewSet

router = SimpleRouter()
router.register('api/exchange', ExchangeViewSet, basename='exchange')
router.register('api/category', CategoryViewSet, basename='category')
router.register('api/subcategory', SubCategoryViewSet, basename='subcategory')
router.register('api/exchange-reviews', ExchangeReviewViewSet, basename='exchange-reviews')
router.register('api/quotes', ExchangeQuoteViewSet, basename='quotes')
router.register('api/admin-exchange', AdminExchangeViewSet, basename='admin-exchange')

# Booking system routes
router.register('api/business-hours', BusinessHoursViewSet, basename='business-hours')
router.register('api/time-slots', TimeSlotViewSet, basename='time-slots')
router.register('api/bookings', BookingViewSet, basename='bookings')

urlpatterns = router.urls
