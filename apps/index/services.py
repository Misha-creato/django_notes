from typing import Any

from django.contrib import messages

from notes.models import Note


def get_notes(request: Any) -> Note | None:
    try:
        notes = Note.objects.filter(
            author=request.user,
        )
    except Exception as exc:
        print(f'Возникла ошибка при получении списка заметок {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return None
    return notes
