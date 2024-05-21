from django.shortcuts import (
    render,
    redirect,
)
from django.views import View


from users.services import register_user, login_user, confirm_email


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
        return redirect('login') #index


class RegisterView(View):
    def post(self, request):
        status = register_user(
            request=request,
        )
        return redirect('login')


class ConfirmEmailView(View):
    def get(self, request, url_hash):
        confirm_email(
            request=request,
            url_hash=url_hash,
        )
        return redirect('login')# index
