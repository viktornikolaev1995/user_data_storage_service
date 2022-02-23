from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions

from .custom_permissions import CustomPermissions
from .models import MyUser
from .serializers import MyUserSerializer


def check_is_admin():
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = CustomPermissions
            print(self.permission_classes)
        return decorated_func
    return decorator


class MyUserListCreateAPIView(generics.ListCreateAPIView):
    """All users except users with status is_superuser"""
    queryset = MyUser.objects.filter(is_superuser=False)

    serializer_class = MyUserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @method_decorator(check_is_admin())
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


