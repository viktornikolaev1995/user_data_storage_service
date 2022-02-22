
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, User, PermissionsMixin
)
from django.utils import timezone


class MyUserManager(BaseUserManager):
    def create_user(self, email, user_name, birthday, password=None, **other_fields):
        """
        Creates and saves a User with the given email, birthday and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not user_name:
            raise ValueError('Users must have an user name')

        user = self.model(
            email=self.normalize_email(email),
            user_name=user_name,
            birthday=birthday,
            **other_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, user_name, birthday, password=None, **other_fields):
        """
        Creates and saves a superuser with the given email, username, date of
        birth and password.
        """
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must assigned to is_staff=True.')

        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must assigned to is_superuser=True.')

        return self.create_user(email, user_name, birthday, password, **other_fields)


class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True)
    user_name = models.CharField(verbose_name='Username', max_length=255, unique=True)
    first_name = models.CharField(verbose_name='First name', max_length=255, blank=True)
    last_name = models.CharField(verbose_name='Last name', max_length=255, blank=True)
    other_name = models.CharField(verbose_name='Other name', max_length=255, blank=True)
    phone = models.CharField(verbose_name='Phone', max_length=50, blank=True)
    birthday = models.DateField(verbose_name='Birthday')
    city = models.CharField(verbose_name='City', max_length=255, blank=True)
    additional_info = models.TextField(verbose_name='Additional Info', max_length=1000, blank=True)
    data_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['birthday']

    def get_full_name(self):
        # The user is identified by their email address
        return f'{self.email} - {self.username}'

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

