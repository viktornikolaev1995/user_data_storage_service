from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('users/current/', CurrentUserAPIView.as_view(), name='current_user'),
    path('users/', UsersListAPIView.as_view(), name='users'),
    path('user/<int:pk>/', UpdateUserAPIView.as_view(), name='update_user'),
    path('private/users/', PrivateUsersListCreateAPIView.as_view(), name='private_users'),
    path('private/users/<int:pk>/', PrivateUserDetailRetrieveUpdateDestroyAPIView.as_view(), name='private_user')
]
