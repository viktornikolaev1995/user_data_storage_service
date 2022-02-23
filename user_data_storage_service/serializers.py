from rest_framework import serializers
from .models import MyUser


class MyUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'last_name', 'other_name', 'email', 'phone', 'birthday', 'city',
                  'additional_info', 'is_admin']
