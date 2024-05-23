from typing import Any

from django.contrib import messages

from notes.forms import NoteForm
from notes.models import Note

from users.services import set_form_messages


def get_note(request: Any, slug: str) -> (int, Note | None):
    print(f'Поиск заметки {slug}')
    author = request.user
    try:
        note = Note.objects.filter(
            author=author,
            slug=slug,
        ).first()
    except Exception as exc:
        print(f'Ошибка при попытке найти заметку {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return 500, None

    if note is None:
        print(f'Не удалось найти заметку {slug}')
        messages.error(
            request=request,
            message='Не удалось найти заметку',
        )
        return 404, None

    print('Заметка найдена')
    return 200, note


def edit_note(request: Any, slug: str) -> (int, str):
    status, note = get_note(
        request=request,
        slug=slug,
    )
    if status != 200:
        return status, None

    status, slug = edit_or_create_note(
        request=request,
        note=note,
    )

    if status != 200:
        return status, note.slug

    print(f'Заметка {note} изменена')
    messages.success(
        request=request,
        message='Заметка успешно изменена',
    )
    return status, slug


def create_note(request: Any) -> (int, str):
    status, slug = edit_or_create_note(
        request=request,
    )
    if status == 200:
        messages.success(
            request=request,
            message='Заметка успешно создана',
        )
    return status, slug


def edit_or_create_note(request: Any, note: Note = None) -> (int, str):
    data = request.POST
    print(f'Редактирование или создание заметки {data}')
    form = NoteForm(data, note)
    if not form.is_valid():
        print(f'Невалидные данные {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400, None

    try:
        form.instance.author = request.user
        form.save()
    except Exception as exc:
        print(f'Возникла ошибка при сохранении изменений заметки {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return 500, None
    return 200, form.instance.slug


def delete_note(request: Any, slug: str) -> int:
    status, note = get_note(
        request=request,
        slug=slug,
    )
    if status != 200:
        return status

    try:
        note.delete()
    except Exception as exc:
        print(f'Возникла ошибка при удалении заметки {exc}')
        messages.error(
            request=request,
            message='Не удалось удалить заметку',
        )
        return 500

    print(f'Заметка успешно удалена')
    messages.success(
        request=request,
        message='Заметка успешно удалена',
    )
    return 200