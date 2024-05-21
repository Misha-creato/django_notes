from django.urls import path

from users.views import (
    LoginView,
    RegisterView,
    ConfirmEmailView,
)


urlpatterns = [
    path(
        'login/',
        LoginView.as_view(),
        name='login',
    ),
    path(
        'register/',
        RegisterView.as_view(),
        name='register',
    ),
    path(
        'confirm_email/<str:url_hash>/',
        ConfirmEmailView.as_view(),
        name='confirm_email',
    ),
]
