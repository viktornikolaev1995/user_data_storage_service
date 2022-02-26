from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils import timezone


class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None, **other_fields):
        """Creates and saves a User with the given email, first_name and password."""
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            **other_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password=None, **other_fields):
        """Creates and saves a superuser with the given email, first_name and password."""
        other_fields.setdefault('is_admin', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_admin') is not True:
            raise ValueError('Superuser must assigned to is_admin=True.')

        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must assigned to is_superuser=True.')

        return self.create_user(email, first_name, password, **other_fields)


class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True)
    first_name = models.CharField(verbose_name='First name', max_length=255)
    last_name = models.CharField(verbose_name='Last name', max_length=255, blank=True)
    other_name = models.CharField(verbose_name='Other name', max_length=255, blank=True)
    photo = models.ImageField(verbose_name='Photo', upload_to='users/%Y/%m/%d/', blank=True, null=True)
    phone = models.CharField(verbose_name='Phone', max_length=50, blank=True)
    birthday = models.DateField(verbose_name='Birthday', blank=True, null=True)
    city = models.CharField(verbose_name='City', max_length=255, blank=True)
    additional_info = models.TextField(verbose_name='Additional Info', max_length=1000, blank=True)
    data_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        """The user is identified by their email address"""
        return self.email

    def get_short_name(self):
        """The user is identified by their email address"""
        return self.email

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        """All admins should be a staff"""
        return self.is_admin
