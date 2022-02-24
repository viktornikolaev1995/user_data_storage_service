from rest_framework import generics, permissions, mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import AuthorOrReadOnly
from .models import MyUser
from .serializers import UsersListSerializer, UpdateUserSerializer, PrivateUsersListSerializer, \
    PrivateUserDetailSerializer, PrivateCreateUserSerializer, CurrentUserSerializer


class CurrentUserAPIView(APIView):
    """Current user"""
    def get(self, request):
        user = MyUser.objects.get(id=request.user.id)
        serializer = CurrentUserSerializer(user)
        return Response(serializer.data)


class UsersListAPIView(generics.ListAPIView):
    """List of users with short information about themself"""
    queryset = MyUser.objects.all()
    serializer_class = UsersListSerializer
    permission_classes = [permissions.IsAuthenticated]


class UpdateUserAPIView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericAPIView):
    """User can update info about only yourself"""
    queryset = MyUser.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = [AuthorOrReadOnly]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class PrivateUsersListCreateAPIView(generics.ListCreateAPIView):
    """List of users which can be viewed by admin and also admin can create an user"""
    queryset = MyUser.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = PrivateUserDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            serializer_class = PrivateCreateUserSerializer
        else:
            serializer_class = PrivateUsersListSerializer
        return serializer_class


class PrivateUserDetailRetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                                                    mixins.DestroyModelMixin, GenericAPIView):
    """User, which can be retrieve, update or destroy by admin"""
    queryset = MyUser.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            self.serializer_class = PrivateUserDetailSerializer
        elif self.request.method == 'PATCH':
            self.serializer_class = UpdateUserSerializer
        return self.serializer_class


