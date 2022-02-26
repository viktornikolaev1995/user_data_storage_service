from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class AuthorOrReadOnly(permissions.BasePermission):
    """Custom permission"""

    def has_permission(self, request, view):
        if request.method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']:
            return False

        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True
        return False
