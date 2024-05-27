from django.contrib.auth import logout
from django.shortcuts import (
    render,
    redirect,
)
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from users.services import (
    register_user,
    login_user,
    confirm_email,
    send_confirmation_email,
    change_password,
    password_reset_request,
    password_reset,
    get_user_by_hash,
)


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request=request,
            template_name='login.html'
        )

    def post(self, request):
        status = login_user(
            request=request,
        )
        if status != 200:
            return redirect('login')
        return redirect('index')


class RegisterView(View):
    def post(self, request):
        register_user(
            request=request,
        )
        return redirect('login')


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(
            request=request,
        )
        return redirect('login')


class ConfirmEmailView(View):
    def get(self, request, url_hash):
        confirm_email(
            request=request,
            url_hash=url_hash,
        )
        return redirect('index')


class SendConfirmEmailView(LoginRequiredMixin, View):
    def post(self, request):
        send_confirmation_email(
            request=request,
            user=request.user,
        )
        return redirect('index')


class SettingsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(
            request=request,
            template_name='settings.html',
        )

    def post(self, request):
        change_password(
            request=request,
        )
        return redirect('settings')


class PasswordResetRequestView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request=request,
            template_name='password_reset_request.html',
        )

    def post(self, request):
        status = password_reset_request(
            request=request,
        )
        if status != 200:
            return redirect('password_reset_request')
        return redirect('login')


class PasswordResetView(View):
    def get(self, request, url_hash):
        status, user = get_user_by_hash(
            request=request,
            url_hash=url_hash,
        )
        if status != 200:
            return redirect('index')
        return render(
            request=request,
            template_name='password_reset.html',
        )

    def post(self, request, url_hash):
        status = password_reset(
            request=request,
            url_hash=url_hash,
        )
        if status != 200:
            return redirect('password_reset', url_hash)
        return redirect('login')
