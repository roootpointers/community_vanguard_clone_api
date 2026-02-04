from rest_framework import permissions


class CustomPermission(permissions.BasePermission):
    """
    Custom permission class for user-related actions.
    """

    def has_permission(self, request, view):
        """
        Check if the request should be permitted.
        """
        # Allow unrestricted access for these actions: list, get_all_epoxy_systems, retrieve
        if view.action in ['email_signup', 'social_signup', 'email_login', 'social_login', 'admin_login']:
            return True
        # Apply default permissions for other actions
        return request.user and request.user.is_authenticated