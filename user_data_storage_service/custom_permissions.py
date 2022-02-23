from rest_framework import permissions


class CustomPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)