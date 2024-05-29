from django.db import models
from solo.models import SingletonModel


class Configuration(SingletonModel):
    send_emails = models.BooleanField(
        verbose_name='Отправка писем включена',
        default=False,
    )

    class Meta:
        db_table = 'configurations'
        verbose_name = 'Настройки'
