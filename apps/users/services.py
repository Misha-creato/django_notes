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
from django.urls import reverse

from notifications.services import send_email_by_type

from users.forms import (
    CustomUserCreationForm,
    LoginForm,
    PasswordResetRequestForm,
)
from users.models import CustomUser


def register_user(request: Any) -> int:
    data = request.POST
    email = data.get('email')
    print(f'Регистрация пользователя {email}')
    form = CustomUserCreationForm(data)
    if not form.is_valid():
        print(f'Невалидные данные для регистрации пользователя {email}: {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400

    try:
        user = form.save() # commit false
    except Exception as exc:
        print(f'Произошла ошибка при регистрации пользователя {data}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка при создании пользователя',
        )
        return 500

    messages.success(
        request=request,
        message='Пользователь успешно зарегистрирован'
    )
    print(f'Пользователь {user} успешно зарегистрирован')

    send_confirmation_email(
        request=request,
        user=user,
    )

    return 200


def login_user(request: Any) -> int:
    data = request.POST
    email = data.get('email')
    print(f'Вход пользователя {email}')
    form = LoginForm(data)
    if not form.is_valid():
        print(f'Невалидные данные для входа пользователя {email}: {form.errors}')
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
        print(f'Ошибка аутентификации пользователя {email}')
        return 401

    login(
        request=request,
        user=user,
    )
    print(f'Пользователь {user} успешно вошел в систему')
    return 200


def confirm_email(request: Any, url_hash: str) -> int:
    print(f'Подтверждение адреса электронной почты польхователя с хэшем: {url_hash}')
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
        print(f'Возникла ошибка при подтверждении адреса электронной почты пользователя {user}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка при подтверждении адреса электронной почты',
        )
        return 500

    messages.success(
        request=request,
        message='Адрес электронной почты успешно подтвержден'
    )
    print(f'Адрес электронной почты пользователя {user} успешно подтвержден')
    return 200


def change_password(request: Any) -> int:
    data = request.POST
    user = request.user
    print(f'Настройки изменения пароля для пользователя {user}')
    form = PasswordChangeForm(data=data, user=user)
    if not form.is_valid():
        print(f'Невалидные данные для смены пароля пользователя {user}: {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400

    try:
        form.save()
    except Exception as exc:
        print(f'Возникла ошибка при изменении пароля пользователя {user}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка при изменении пароля',
        )
        return 500

    print(f'Пароль пользователя {user} успешно изменен')
    messages.success(
        request=request,
        message='Пароль успешно изменен',
    )
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
        print(f'Невалидные данные для запроса на восстановление пароля: {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400

    email = form.cleaned_data['email']
    try:
        user = CustomUser.objects.filter(email=email).first()
    except Exception as exc:
        print(f'Возникла ошибка при попытке найти пользователя {email}: {exc}')
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
    print(f'Сброс пароля для пользователя c хэшем: {url_hash}')
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
        print(f'Невалидные данные для сброса пароля пользователя {user}: {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400

    form.user.url_hash = None
    try:
        form.save()
    except Exception as exc:
        print(f'Возникла ошибка при сохранении формы смены пароля для пользователя {user}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка при восстановлении пароля'
        )
        return 500

    messages.success(
        request=request,
        message='Пароль успешно восстановлен'
    )
    print(f'Пароль пользователя {user} успешно восстановлен')
    return 200


def get_user_by_hash(request: Any, url_hash: str) -> (int, CustomUser | None):
    print(f'Получение пользователя по хэшу {url_hash}')
    try:
        user = CustomUser.objects.filter(url_hash=url_hash).first()
    except Exception as exc:
        print(f'Возникла ошибка при поиске пользователя по хэшу {url_hash}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка'
        )
        return 500, None

    if user is None:
        print(f'Пользователь с хэшем {url_hash} не найден')
        messages.error(
            request=request,
            message='Неверный токен'
        )
        return 404, None

    print(f'Пользователь {user} с хэшем {url_hash} найден')
    return 200, user


def send_confirmation_email(request: Any, user: CustomUser) -> int:
    print(f'Подготовка отправки письма для подтверждения адреса электронной почты пользователю {user}')
    status = get_mail_response_status(
        request=request,
        user=user,
        email_type='confirm_email',
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
        print(f'Возникла ошибка при сохранении изменений поля mail_sent для пользователя {user}: {exc}')
        return 500

    messages.success(
        request=request,
        message='Письмо для подтверждения адреса электронной почты отправлено',
    )
    return 200


def send_password_reset_email(request: Any, user: CustomUser) -> int:
    print(f'Подготовка отправки письма для сброса пароля пользователю {user}')
    status = get_mail_response_status(
        request=request,
        user=user,
        email_type='password_reset',
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


def get_mail_response_status(request: Any, user: CustomUser, email_type: str) -> int:
    status, mail_data = get_mail_data(
        request=request,
        user=user,
        email_type=email_type,
    )
    if status == 200:
        status = send_email_by_type(
            user=user,
            mail_data=mail_data,
            email_type=email_type,
        )
        if status == 403:
            messages.warning(
                request=request,
                message='Функция отправки писем отключена',
            )
    return status


def get_mail_data(request: Any, user: CustomUser, email_type: str) -> (int, dict | None):
    print(f'Получение данных для формирования текста письма {email_type} пользователю {user}')
    status, url_hash = set_url_hash(
        user=user,
    )
    if status != 200:
        print(f'Не удалось получить данные для формирования '
              f'текста письма {email_type} пользователю {user}'
              )
        return status, None

    url = request.build_absolute_uri(reverse(email_type, args=(url_hash,)))
    mail_data = {
        'url': url,
    }

    print(f'Данные для формирования текста письма {email_type} '
          f'пользователю {user} получены: {mail_data}'
          )
    return 200, mail_data


def set_url_hash(user: CustomUser) -> (int, str):
    print(f'Установка хэша для пользователя {user}')
    url_hash = str(uuid.uuid4())
    user.url_hash = url_hash

    try:
        user.save()
    except Exception as exc:
        print(f'Не удалось установить хэш для пользователя {user}: {exc}')
        return 500, None

    print(f'Хэш для пользователя {user} установлен')
    return 200, url_hash


def set_form_messages(request: Any, form: Any):
    for errors in form.errors.values():
        for error in errors:
            messages.error(
                request=request,
                message=error,
            )