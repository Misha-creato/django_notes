from django.urls import path

from users.views import (
    LoginView,
    LogoutView,
    RegisterView,
    ConfirmEmailView,
    SendConfirmEmailView,
    SettingsView,
    PasswordResetRequestView,
    PasswordResetView,
)


urlpatterns = [
    path(
        'login/',
        LoginView.as_view(),
        name='login',
    ),
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout',
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
    path(
        'send_confirm_email/',
        SendConfirmEmailView.as_view(),
        name='send_confirm_email',
    ),
    path(
        'settings/',
        SettingsView.as_view(),
        name='settings',
    ),
    path(
        'password/reset/request/',
        PasswordResetRequestView.as_view(),
        name='password_reset_request',
    ),
    path(
        'password/reset/<str:url_hash>/',
        PasswordResetView.as_view(),
        name='password_reset',
    ),
]
