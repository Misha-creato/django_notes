from django.core.mail import send_mail

from config.settings import (
    SEND_EMAILS,
    EMAIL_HOST_USER,
)
from notifications.models import EmailTemplate
from users.models import CustomUser


def send_email_by_type(user: CustomUser, mail_data: dict, email_type: str) -> int:
    email_text = formate_email_text(
        mail_data=mail_data,
        email_type=email_type,
    )
    if not email_text:
        return 500

    status = send_email_to_user(
        user=user,
        email_text=email_text,
    )
    return status


def formate_email_text(mail_data: dict, email_type: str) -> dict:
    print(f'Формирование текста для письма {email_type}')
    try:
        mail = EmailTemplate.objects.filter(email_type=email_type).first()
    except Exception as exc:
        print(f'Возникла ошибка при поиске шаблона письма {email_type}: {exc}')
        return {}

    if mail is None:
        print(f'Шаблон письма {email_type} не найден')
        return {}

    subject = mail.subject
    try:
        message = mail.message.format(**mail_data)
    except Exception as exc:
        print(f'Возникла ошибка при форматировании текста для письма {email_type}: {exc}')
        return {}

    print(f'Текст для письма {email_type} успешно сформирован')
    return {
        'subject': subject,
        'message': message,
    }


def send_email_to_user(user: CustomUser, email_text: dict) -> int:
    if not SEND_EMAILS:
        print('Отправка писем отключена')
        return 403

    subject = email_text["subject"]
    print(f'Отправка письма {subject} пользователю {user}')
    try:
        send_mail(
            subject=subject,
            message=email_text['message'],
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
    except Exception as exc:
        print(f'Произошла ошибка при отправке письма {subject} пользователю {user}: {exc}')
        return 500

    print(f'Письмо {subject} пользователю {user} успешно отправлено')
    return 200
