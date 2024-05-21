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


class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
    )
    password = forms.PasswordInput()
