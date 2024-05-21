import json
import os
import uuid

from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.urls import reverse

from config.settings import (
    SEND_EMAILS,
    EMAIL_HOST_USER,
)

from users.forms import CustomUserCreationForm, CustomLoginForm
from users.models import CustomUser


CUR_DIR = os.path.dirname(__file__)


def register_user(request: Any) -> int:
    data = request.POST
    form = CustomUserCreationForm(data)
    if not form.is_valid():
        print(f'Невалидные данные {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400
    try:
        print('Регистрация пользователя')
        user = form.save() # commit false
    except Exception as exc:
        print(f'Произошла ошибка при регистрации пользователя: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка при создании пользователя',
        )
        return 500
    messages.success(
        request=request,
        message='Пользователь успешно создан'
    )
    send_confirmation_email(
        request=request,
        user=user,
    )
    return 200


def login_user(request: Any) -> int:
    data = request.POST
    form = CustomLoginForm(data)
    if not form.is_valid():
        return 400
    user = authenticate(
        request=request,
        email=data['email'],
        password=data['password'],
    )
    if user is None:
        messages.error(
            request=request,
            message='Неправильные адрес электронной почты или пароль'
        )
        return 401
    login(
        request=request,
        user=user,
    )
    return 200


def confirm_email(request: Any, url_hash: str) -> int:
    try:
        user = CustomUser.objects.filter(url_hash=url_hash).first()
    except Exception as exc:
        print(f'Возникла ошибка при поиске пользователя')
        return 500
    if user is None:
        messages.error(
            request=request,
            message='Неверный токен'
        )
        return 404
    user.url_hash = None
    user.email_confirmed = True
    user.save()
    messages.success(
        request=request,
        message='Адрес электронной почты успешно подтвержден'
    )
    return 200


def prepare_email_text(request: Any, user: CustomUser, action: str) -> dict | None:
    status = set_url_hash(
        user=user,
    )
    if status != 200:
        return None

    with open(f'{CUR_DIR}/mail_messages/{action}.json') as file:
        data = json.load(file)

    url = request.build_absolute_uri(reverse(action, args=(user.url_hash, )))

    subject = data['subject']
    message = data['message'].format(url=url)
    success_message = data['success_message']

    return {
        'subject': subject,
        'message': message,
        'success_message': success_message,
    }


def send_email_to_user(request: Any, user: CustomUser, email_text: dict) -> int:
    if not SEND_EMAILS:
        print('Отправка писем отключена')
        return 203
    try:
        send_mail(
            subject=email_text['subject'],
            message=email_text['message'],
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        messages.success(
            request=request,
            message=email_text['success_message'],
        )
    except Exception as exc:
        print(f'Произошла ошибка при отправке письма пользователю {exc}')
        messages.warning(
            request=request,
            message=email_text['fail_message'],
        )
        return 202
    return 200


def send_confirmation_email(request: Any, user: CustomUser):
    email_text = prepare_email_text(
        request=request,
        user=user,
        action='confirm_email',
    )
    status = send_email_to_user(
        request=request,
        user=user,
        email_text=email_text,
    )
    if status == 200:
        user.mail_sent = True
        user.save()


def set_url_hash(user: CustomUser) -> int:
    url_hash = str(uuid.uuid4())
    user.url_hash = url_hash
    try:
        user.save()
    except Exception as exc:
        print('Не удалось установить хэш для пользователя')
        return 500
    return 200


def set_form_messages(request: Any, form: Any):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(
                request=request,
                message=error,
            )
