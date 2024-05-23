from django.contrib.auth.forms import (
    BaseUserCreationForm,
)
from django import forms

from users.models import CustomUser


class CustomUserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'password1',
            'password2',
        )


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
    )
    password = forms.PasswordInput()


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        required=True,
    )