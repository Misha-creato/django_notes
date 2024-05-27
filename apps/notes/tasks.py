from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from workers import task

from notes.models import Note
from notes.services import send_notification_email

from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def time_to_send_notification(self, note_id: int):
    note = Note.objects.filter(id=note_id).first()
    print('Селери отправляет письмо')
    status = send_notification_email(note)
    if status != 200:
        try:
            print(f"Попытка отправить письмо еще раз")
            self.retry()
        except MaxRetriesExceededError:
            print(f"Попытки закончились. Письмо не удалось отправить")


@task(schedule=60)
def check_notification_date():
    notes = Note.objects.filter(notify_at__date=timezone.now().date(), notification_sent=False)
    for note in notes:
        if note.notify_at == timezone.now().replace(second=0, microsecond=0):
            print("Воркер нашел совпадение")
            time_to_send_notification.delay(note_id=note.id)
