from django.core.mail import send_mail

from config.settings import SEND_EMAILS, EMAIL_HOST_USER
from notifications.models import EmailTemplate
from users.models import CustomUser


def send_email_by_action(user: CustomUser, mail_data: dict, action: str) -> int:
    email_text = prepare_email_text(
        mail_data=mail_data,
        action=action,
    )
    if email_text is None:
        return 500
    status = send_email_to_user(
        user=user,
        email_text=email_text,
    )
    return status


def prepare_email_text(mail_data: dict, action: str) -> dict | None:
    print(f'Формирование текста для письма {action}')
    try:
        mail = EmailTemplate.objects.filter(email_type=action).first()
        subject = mail.subject
        message = mail.message.format(**mail_data)
    except Exception as exc:
        print(f'Возникла ошибка при формировании текста для письма {action}: {exc}')
        return None

    print(f'Текст для письма {action} успешно сформирован')
    return {
        'subject': subject,
        'message': message,
    }


def send_email_to_user(user: CustomUser, email_text: dict) -> int:
    if not SEND_EMAILS:
        print('Отправка писем отключена')
        return 403

    print(f'Отправка письма {email_text["subject"]} пользователю {user}')
    try:
        send_mail(
            subject=email_text['subject'],
            message=email_text['message'],
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
    except Exception as exc:
        print(f'Произошла ошибка при отправке письма {email_text["subject"]} пользователю {user}: {exc}')
        return 500

    print(f'Письмо {email_text["subject"]} пользователю {user} успешно отправлено')
    return 200
