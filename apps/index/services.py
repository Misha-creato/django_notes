from typing import Any

from django.contrib import messages

from notes.models import Note


def get_notes(request: Any) -> [Note]:
    print(f'Получение списка заметок пользователя {request.user}')
    try:
        notes = Note.objects.filter(
            author=request.user,
        )
    except Exception as exc:
        print(f'Возникла ошибка при получении списка заметок пользователя {request.user}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return []
    print(f'Список заметок пользователя {request.user} получен')
    return notes
