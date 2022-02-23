from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('users/', MyUserListCreateAPIView.as_view(), name='users'),
]