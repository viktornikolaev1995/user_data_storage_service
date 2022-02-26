import jwt
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
import datetime
from .permissions import AuthorOrReadOnly
from .models import MyUser
from .serializers import UsersListSerializer, UpdateUserSerializer, PrivateUsersListSerializer, \
    PrivateUserDetailSerializer, PrivateCreateUserSerializer, CurrentUserSerializer, LoginSerializer


class Mixin(APIView):
    queryset = MyUser.objects.all().order_by('id')

    def check_authentication_failed(self, request):
        """if a token does not locate in Cookies or id from Cookies don't match with the current user id from request,
        returns AuthenticationFailed error"""
        encode_token = request.COOKIES.get('jwt')

        if encode_token is None:
            return self.handle_exception(AuthenticationFailed)
        decode_token = jwt.decode(encode_token, 'secret', algorithms=['HS256'])

        if request.user.id != decode_token['id']:
            return self.handle_exception(AuthenticationFailed)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['user'],
    operation_description="Здесь находится вся информация, доступная пользователю о самом себе, "
                          "а так же информация является ли он администратором",
    operation_id="current_user_users_current_get",
    operation_summary="Получение данных о текущем пользователе",
    responses={'200': 'Successful Response', '400': 'Bad Request', '401': 'Unauthorized'}
))
class CurrentUserAPIView(Mixin):
    """Получение данных о текущем пользователе. Здесь находится вся информация, доступная пользователю о самом себе,
    а так же информация является ли он администратором"""

    def get(self, request):
        self.check_authentication_failed(request)
        user = MyUser.objects.get(id=request.user.id)
        serializer = CurrentUserSerializer(user)
        return Response(serializer.data)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['user'],
    operation_description="Здесь находится вся информация, доступная пользователю о других пользователях",
    operation_id="users_users_get",
    operation_summary="Постраничное получение кратких данных обо всех пользователях",
    responses={'200': 'Successful Response', '400': 'Bad Request', '401': 'Unauthorized', '422': 'Validation Error'}
))
class UsersListAPIView(Mixin, generics.ListAPIView):
    """Постраничное получение кратких данных обо всех пользователях. Здесь находится вся информация, доступная
    пользователю о других пользователях"""

    serializer_class = UsersListSerializer

    def get(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return super().get(self, request, *args, **kwargs)


@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['user'],
    operation_description="Здесь пользователь имеет возможность изменить свои данные",
    operation_id="edit_user_users__pk__patch",
    operation_summary="Изменение данных пользователя",
    responses={'200': 'Successful Response', '400': 'Bad Request', '401': 'Unauthorized', '404': 'Not Found',
               '422': 'Validation Error'}
))
class UpdateUserAPIView(Mixin, mixins.UpdateModelMixin, GenericAPIView):
    """Изменение данных пользователя. Здесь пользователь имеет возможность изменить свои данные"""

    serializer_class = UpdateUserSerializer
    permission_classes = [AuthorOrReadOnly]

    def patch(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.partial_update(request, *args, **kwargs)


class PrivateUsersListCreateAPIView(Mixin, generics.ListCreateAPIView):
    """Постраничное получение кратких данных обо всех пользователях. Здесь находится вся информация, доступная
    пользователю о других пользователях"""

    permission_classes = [permissions.IsAdminUser]

    @method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['admin'],
        operation_description="Здесь находится вся информация, доступная пользователю о других пользователях",
        operation_id="private_users_private_users_get",
        operation_summary="Постраничное получение кратких данных обо всех пользователях",
        responses={'200': 'Successful Response', '400': 'Bad Request', '401': 'Unauthorized', '403': 'Forbidden',
                   '422': 'Validation Error'}
    ))
    def get(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return super().list(request, *args, **kwargs)

    @method_decorator(name='post', decorator=swagger_auto_schema(
        tags=['admin'],
        operation_description="Здесь возможно занести в базу нового пользователя с минимальной информацией о нем",
        operation_id="private_create_users_private_users_post",
        operation_summary="Создание пользователя",
        responses={'201': 'Successful Response', '400': 'Bad Request', '401': 'Unauthorized', '403': 'Forbidden',
                   '422': 'Validation Error'}
    ))
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


class PrivateUserDetailRetrieveUpdateDestroyAPIView(Mixin, mixins.RetrieveModelMixin,
                                                    mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    """Детальное получение информации о пользователе. Здесь администратор может увидеть всю существующую
    пользовательскую информацию"""

    permission_classes = [permissions.IsAdminUser]

    @method_decorator(name='get', decorator=swagger_auto_schema(
        tags=['admin'],
        operation_description="Здесь администратор может увидеть всю существующую пользовательскую информацию",
        operation_id="private_get_user_private_users__pk__get",
        operation_summary="Детальное получение информации о пользователе",
        responses={'200': 'Successful Response', '400': 'Bad Request', '401': 'Unauthorized', '403': 'Forbidden',
                   '404': 'Not Found', '422': 'Validation Error'}
    ))
    def get(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.retrieve(request, *args, **kwargs)

    @method_decorator(name='patch', decorator=swagger_auto_schema(
        tags=['admin'],
        operation_description="Здесь администратор может изменить любую информацию о пользователе",
        operation_id="private_patch_user_private_users__pk__patch",
        operation_summary="Изменение информации о пользователе",
        responses={'200': 'Successful Response', '400': 'Bad Request', '401': 'Unauthorized', '403': 'Forbidden',
                   '404': 'Not Found', '422': 'Validation Error'}
    ))
    def patch(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.partial_update(request, *args, **kwargs)

    @method_decorator(name='delete', decorator=swagger_auto_schema(
        tags=['admin'],
        operation_description="Удаление пользователя",
        operation_id="private_delete_user_private_users__pk__delete",
        operation_summary="Удаление пользователя",
        responses={'204': 'Successful Response', '401': 'Unauthorized', '403': 'Forbidden', '422': 'Validation Error'}
    ))
    def delete(self, request, *args, **kwargs):
        self.check_authentication_failed(request)
        return self.destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            self.serializer_class = PrivateUserDetailSerializer
        elif self.request.method == 'PATCH':
            self.serializer_class = UpdateUserSerializer
        return self.serializer_class


@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['auth'],
    operation_description="После успешного входа в систему необходимо установить Cookies для пользователя",
    operation_id="login_login_post",
    operation_summary="Вход в систему",
    responses={'200': 'Successful Response', '400': 'Bad Request', '422': 'Validation Error'}
))
class LoginAPIView(GenericAPIView):
    """Вход в систему"""

    serializer_class = LoginSerializer

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


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['auth'],
    operation_description="При успешном выходе необходимо удалить установленные Cookies",
    operation_id="logout_logout_get",
    operation_summary="Выход из системы",
    responses={'200': 'Successful Response'}
))
class LogoutAPIView(APIView):
    """Выход из системы"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logout(request)

        data = {
            'message': 'Выход из системы'
        }
        response = Response(data, status=status.HTTP_200_OK)
        response.delete_cookie('jwt')

        return response
