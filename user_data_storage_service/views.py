import jwt
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
import datetime
from .permissions import AuthorOrReadOnly
from .models import MyUser
from .serializers import UsersListSerializer, UpdateUserSerializer, PrivateUsersListSerializer, \
    PrivateUserDetailSerializer, PrivateCreateUserSerializer, CurrentUserSerializer


class AuthenticationFailedMixin(APIView):
    def check_authentication_failed(self, request):
        """if a token does not locate in Cookies returns AuthenticationFailed error"""
        encode_token = request.COOKIES.get('jwt')
        if encode_token is None:
            return self.handle_exception(AuthenticationFailed)


class CurrentUserAPIView(AuthenticationFailedMixin):
    """Current user"""

    def get(self, request):
        self.check_authentication_failed(request)
        user = MyUser.objects.get(id=request.user.id)
        serializer = CurrentUserSerializer(user)
        return Response(serializer.data)


class UsersListAPIView(AuthenticationFailedMixin, generics.ListAPIView):
    """List of users with short information about themself"""
    queryset = MyUser.objects.all()
    serializer_class = UsersListSerializer

    def get(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return super().get(self, request, *args, **kwargs)


class UpdateUserAPIView(AuthenticationFailedMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericAPIView):
    """User can update info about only yourself"""
    queryset = MyUser.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = [AuthorOrReadOnly]

    def get(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.partial_update(request, *args, **kwargs)


class PrivateUsersListCreateAPIView(AuthenticationFailedMixin, generics.ListCreateAPIView):
    """List of users which can be viewed by admin and also admin can create an user"""
    queryset = MyUser.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return super().list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return super().create(request, *args, **kwargs)

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


class PrivateUserDetailRetrieveUpdateDestroyAPIView(AuthenticationFailedMixin, mixins.RetrieveModelMixin,
                                                    mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    """User, which can be retrieve, update or destroy by admin"""
    queryset = MyUser.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            self.serializer_class = PrivateUserDetailSerializer
        elif self.request.method == 'PATCH':
            self.serializer_class = UpdateUserSerializer
        return self.serializer_class


class LoginAPIView(APIView):
    """Login by user"""

    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']

            try:
                user = MyUser.objects.get(email=email)
            except ObjectDoesNotExist:
                data = {
                    'error': '"Validation Error (422)'
                }
                return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if user is None or not user.check_password(password):
                data = {
                    'error': '"Validation Error (422)'
                }
                return Response(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            elif user is not None:
                login(request, user)
                data = {
                    'message': 'Вход в систему'
                }
                payload = {
                    'id': user.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                    'iat': datetime.datetime.utcnow()
                }
                encoded_token = jwt.encode(payload, 'secret', algorithm='HS256')

                response = Response(data, status=status.HTTP_200_OK)
                response.set_cookie(key='jwt', value=encoded_token, httponly=True)
                return response

        except KeyError:
            self.handle_exception(ValidationError)


class LogoutAPIView(APIView):
    """Logout by authenticated user"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logout(request)

        data = {
            'message': 'Выход из системы'
        }
        response = Response(data, status=status.HTTP_200_OK)
        response.delete_cookie('jwt')

        return response
