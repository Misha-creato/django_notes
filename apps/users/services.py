import json
import os
import uuid

from typing import Any

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    update_session_auth_hash,
)
from django.contrib.auth.forms import (
    PasswordChangeForm,
    SetPasswordForm,
)
from django.core.mail import send_mail
from django.urls import reverse

from config.settings import (
    SEND_EMAILS,
    EMAIL_HOST_USER,
)

from users.forms import (
    CustomUserCreationForm,
    LoginForm, PasswordResetRequestForm,
)
from users.models import CustomUser


CUR_DIR = os.path.dirname(__file__)


def register_user(request: Any) -> int:
    data = request.POST
    print(f'Регистрация пользователя {data}')
    form = CustomUserCreationForm(data)
    if not form.is_valid():
        print(f'Невалидные данные {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400

    try:
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
    print(f'Пользователь {user} успешно зарегистрирован')

    send_confirmation_email(
        request=request,
        user=user,
    )

    return 200


def login_user(request: Any) -> int:
    data = request.POST
    print(f'Вход пользователя {data}')
    form = LoginForm(data)
    if not form.is_valid():
        print(f'Невалидные данные {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
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
        print('Ошибка аутентификации пользователя')
        return 401

    login(
        request=request,
        user=user,
    )
    print('Пользователь успешно вошел в систему')
    return 200


def confirm_email(request: Any, url_hash: str) -> int:
    print('Подтверждение адреса электронной почты')
    status, user = get_user_by_hash(
        request=request,
        url_hash=url_hash,
    )
    if status != 200:
        return status

    user.url_hash = None
    user.email_confirmed = True
    try:
        user.save()
    except Exception as exc:
        print(f'Возникла ошибка при сохранении изменений полей email_confirmed, url_hash {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка при подтверждении адреса электронной почты',
        )
        return 500

    messages.success(
        request=request,
        message='Адрес электронной почты успешно подтвержден'
    )
    print('Адрес электронной почты успешно подтвержден')
    return 200


def change_password(request: Any) -> int:
    data = request.POST
    user = request.user
    print(f'Настройки изменения пароля {data} для пользователя {user}')
    form = PasswordChangeForm(data=data, user=user)
    if not form.is_valid():
        print(f'Невалидные данные {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400

    form.save()
    messages.success(
        request=request,
        message='Пароль успешно изменен',
    )
    print(f'Пароль успешно изменен')
    update_session_auth_hash(
        request=request,
        user=user,
    )
    return 200


def password_reset_request(request: Any) -> int:
    data = request.POST
    print(f'Запрос на восстановление пароля {data}')
    form = PasswordResetRequestForm(data)
    if not form.is_valid():
        print(f'Невалидные данные {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400

    email = form.cleaned_data['email']
    try:
        user = CustomUser.objects.filter(email=email).first()
    except Exception as exc:
        print(f'Возникла ошибка при попытке найти пользователя {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return 500

    if user is None:
        print(f'Не удалось найти пользователя с таким адресом электронной почты {email}')
        messages.error(
            request=request,
            message='Не удалось найти пользователя с таким адресом электронной почты',
        )
        return 404

    status = send_password_reset_email(
        request=request,
        user=user,
    )
    return status


def password_reset(request: Any, url_hash: str) -> int:
    status, user = get_user_by_hash(
        request=request,
        url_hash=url_hash,
    )
    if status != 200:
        return status

    data = request.POST
    form = SetPasswordForm(
        data=data,
        user=user,
    )
    if not form.is_valid():
        print(f'Невалидные данные {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400

    form.user.url_hash = None
    try:
        form.save()
    except Exception as exc:
        print(f'Возникла ошибка при сохранении формы смены пароля {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка при восстановлении пароля'
        )
        return 500

    messages.success(
        request=request,
        message='Пароль успешно восстановлен'
    )
    print('Пароль успешно восстановлен')
    return 200


def get_user_by_hash(request: Any, url_hash: str) -> (int, CustomUser | None):
    print('Получение пользователя по токену')
    try:
        user = CustomUser.objects.filter(url_hash=url_hash).first()
    except Exception as exc:
        print(f'Возникла ошибка при поиске пользователя {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка'
        )
        return 500, None

    if user is None:
        print(f'Неверный токен {url_hash}')
        messages.error(
            request=request,
            message='Неверный токен'
        )
        return 404, None

    return 200, user


def send_confirmation_email(request: Any, user: CustomUser) -> int:
    status = send_email_by_action(
        request=request,
        user=user,
        action='confirm_email',
    )
    if status != 200:
        messages.error(
            request=request,
            message='Письмо для подтверждения адреса электронной почты не было отправлено',
        )
        return status

    user.mail_sent = True
    try:
        user.save()
    except Exception as exc:
        print(f'Возникла ошибка при сохранении изменений поля mail_sent {exc}')
        return 500

    messages.success(
        request=request,
        message='Письмо для подтверждения адреса электронной почты отправлено',
    )
    return 200


def send_password_reset_email(request: Any, user: CustomUser) -> int:
    status = send_email_by_action(
        request=request,
        user=user,
        action='password_reset',
    )
    if status != 200:
        messages.error(
            request=request,
            message='Письмо для восстановления пароля не было отправлено',
        )
        return status
    messages.success(
        request=request,
        message='Письмо для восстановления пароля отправлено',
    )
    return 200


def send_email_by_action(request: Any, user: CustomUser, action: str) -> int:
    status, url_hash = set_url_hash(
        user=user,
    )
    if status != 200:
        return status

    email_text = prepare_email_text(
        request=request,
        url_hash=url_hash,
        action=action,
    )
    status = send_email_to_user(
        request=request,
        user=user,
        email_text=email_text,
    )
    return status


def prepare_email_text(request: Any, url_hash: str, action: str) -> dict | None:
    with open(f'{CUR_DIR}/mail_messages/{action}.json') as file:
        data = json.load(file)

    url = request.build_absolute_uri(reverse(action, args=(url_hash, )))

    subject = data['subject']
    message = data['message'].format(url=url)

    return {
        'subject': subject,
        'message': message,
    }


def send_email_to_user(request: Any, user: CustomUser, email_text: dict) -> int:
    if not SEND_EMAILS:
        print('Отправка писем отключена')
        messages.warning(
            request=request,
            message='Функция отправки писем отключена',
        )
        return 403

    try:
        send_mail(
            subject=email_text['subject'],
            message=email_text['message'],
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
    except Exception as exc:
        print(f'Произошла ошибка при отправке письма пользователю {exc}')
        return 500

    return 200


def set_url_hash(user: CustomUser) -> (int, str):
    url_hash = str(uuid.uuid4())
    user.url_hash = url_hash
    try:
        user.save()
    except Exception as exc:
        print(f'Не удалось установить хэш для пользователя {user} {exc}')
        return 500, None
    return 200, url_hash


def set_form_messages(request: Any, form: Any):
    for errors in form.errors.values():
        for error in errors:
            messages.error(
                request=request,
                message=error,
            )
