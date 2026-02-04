"""
Models for the Intel app.
"""
from intel.models.intel import Intel, IntelMedia
from intel.models.like import IntelLike
from intel.models.comment import IntelComment, CommentLike
from intel.models.category import IntelCategory

__all__ = ['Intel', 'IntelMedia', 'IntelLike', 'IntelComment', 'CommentLike', 'IntelCategory']
