from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users (superusers or staff) to access.
    """

    def has_permission(self, request, view):
        """
        Check if the request should be permitted.
        Only admin users can access.
        """
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
