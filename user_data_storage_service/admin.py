from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password
from django.forms import TextInput, Textarea
from django.utils.safestring import mark_safe
from .models import *


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'phone', 'birthday', 'city')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        validate_password(password2)
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'phone', 'birthday', 'city')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class MyUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'get_photo', 'is_superuser', 'is_admin', 'is_active', 'data_joined')
    list_filter = ('is_superuser', 'is_admin', 'is_active')
    readonly_fields = ('get_photo',)
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '40'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 6, 'cols': 100})}
    }
    fieldsets = (
        (None, {'fields': ('email', 'password', 'data_joined')}),
        ('Personal info',
         {'fields': (
              ('first_name', 'last_name', 'other_name'),
              ('phone', 'birthday', 'city'),
              ('photo', 'get_photo')
         )}),
        (None, {'fields': ('additional_info',)}),
        ('Permissions', {'fields': ('is_superuser', 'is_admin', 'is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email', 'first_name')
    ordering = ('email', 'first_name')
    filter_horizontal = ()

    def get_photo(self, obj):
        if obj.photo and hasattr(obj.photo, 'url'):
            return mark_safe(f'<img src={obj.photo.url} width="100" height="85"')
        else:
            return mark_safe(f'<img src="#"')

    get_photo.short_description = 'Photo'


admin.site.register(MyUser, MyUserAdmin)

