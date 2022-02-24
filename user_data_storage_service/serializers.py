from rest_framework import serializers
from .models import MyUser


class CurrentUserSerializer(serializers.ModelSerializer):
    """Current user serializer"""

    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'other_name', 'email', 'phone', 'birthday', 'is_admin']


class UsersListSerializer(serializers.ModelSerializer):
    """Users list serializer"""

    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'last_name', 'email']


class PrivateUsersListSerializer(serializers.ModelSerializer):
    """Private users list serializer"""

    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'last_name', 'email']


class PrivateCreateUserSerializer(serializers.ModelSerializer):
    """Private create user serializer"""

    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'email', 'is_admin', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class PrivateUserDetailSerializer(serializers.ModelSerializer):
    """Private user detail serializer"""

    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'last_name', 'other_name', 'email', 'phone', 'birthday', 'city',
                  'additional_info', 'is_admin']


class UpdateUserSerializer(serializers.ModelSerializer):
    """Update user serializer"""

    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'last_name', 'other_name', 'email', 'phone', 'birthday']
