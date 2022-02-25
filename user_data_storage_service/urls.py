from django.urls import re_path
from .views import LoginAPIView, LogoutAPIView, CurrentUserAPIView, UsersListAPIView, UpdateUserAPIView, \
    PrivateUsersListCreateAPIView, PrivateUserDetailRetrieveUpdateDestroyAPIView

urlpatterns = [
    re_path(r'^login/$', LoginAPIView.as_view(), name='login'),
    re_path(r'^logout/$', LogoutAPIView.as_view(), name='logout'),
    re_path(r'^users/current/$', CurrentUserAPIView.as_view(), name='current_user'),
    re_path(r'^users/$', UsersListAPIView.as_view(), name='users'),
    re_path(r'^user/(?P<pk>\d+)/$', UpdateUserAPIView.as_view(), name='update_user'),
    re_path(r'^private/users/$', PrivateUsersListCreateAPIView.as_view(), name='private_users'),
    re_path(r'private/users/(?P<pk>\d+)/$', PrivateUserDetailRetrieveUpdateDestroyAPIView.as_view(),
            name='private_user')
]
