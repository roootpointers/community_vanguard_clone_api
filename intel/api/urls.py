from rest_framework.routers import SimpleRouter
from django.urls import path
from intel.api.views import IntelViewSet, IntelLikeViewSet, IntelCommentViewSet, CommentLikeViewSet, IntelCategoryViewSet
from intel.api.views.admin import AdminIntelViewSet

router = SimpleRouter()
router.register('api/intel', IntelViewSet, basename='intel')
router.register('api/intel-like', IntelLikeViewSet, basename='intel-like')
router.register('api/intel-comment', IntelCommentViewSet, basename='intel-comment')
router.register('api/comment-like', CommentLikeViewSet, basename='comment-like')
router.register('api/intel-category', IntelCategoryViewSet, basename='intel-category')
router.register('api/admin-intel', AdminIntelViewSet, basename='admin-intel')

urlpatterns = router.urls
