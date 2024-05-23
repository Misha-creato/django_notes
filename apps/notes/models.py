import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()


class Note(models.Model):
    author = models.ForeignKey(
        verbose_name='Автор',
        to=User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256,
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True,
    )
    notify_at = models.DateTimeField(
        verbose_name='Дата оповещения',
        null=True,
        blank=True,
    )
    notification_sent = models.BooleanField(
        verbose_name='Оповещение отправлено',
        default=False,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    def __make_slug(self):
        slug_title = slugify(self.title)
        slug_id = str(uuid.uuid4())[:8]
        self.slug = f'{slug_title}-{slug_id}'

    def save(self, *args, **kwargs):
        self.__make_slug()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'notes'
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'
        ordering = [
            'created_at',
        ]
