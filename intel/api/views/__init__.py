"""
Views for the Intel app.
"""
from intel.api.views.intel import IntelViewSet
from intel.api.views.like import IntelLikeViewSet
from intel.api.views.comment import IntelCommentViewSet, CommentLikeViewSet
from intel.api.views.category import IntelCategoryViewSet

__all__ = ['IntelViewSet', 'IntelLikeViewSet', 'IntelCommentViewSet', 'CommentLikeViewSet', 'IntelCategoryViewSet']
