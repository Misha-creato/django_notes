from django.db import models
from solo.models import SingletonModel

from utils.constants import EMAIL_TYPES


class EmailTemplate(models.Model):
    email_type = models.CharField(
        verbose_name='Тип письма',
        max_length=64,
        unique=True,
        choices=EMAIL_TYPES,
    )
    subject = models.CharField(
        verbose_name='Тема',
        max_length=256,
    )
    message = models.TextField(
        verbose_name='Сообщение',
    )

    def __str__(self):
        return self.email_type

    class Meta:
        db_table = 'email_templates'
        verbose_name = 'Шаблон письма'
        verbose_name_plural = 'Шаблоны писем'


class EmailConfiguration(SingletonModel):
    send_emails = models.BooleanField(
        verbose_name='Отправка писем включена',
        default=True,
    )

    def __str__(self):
        return ''

    class Meta:
        db_table = 'email_configurations'
        verbose_name = 'Настройки email'
