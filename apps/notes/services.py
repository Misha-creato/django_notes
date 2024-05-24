from typing import Any

from django.contrib import messages

from notes.forms import NoteForm
from notes.models import Note

from users.services import set_form_messages


def get_note(request: Any, slug: str) -> (int, Note | None):
    author = request.user
    print(f'Поиск заметки {slug} пользователя {author}')
    try:
        note = Note.objects.filter(
            author=author,
            slug=slug,
        ).first()
    except Exception as exc:
        print(f'Ошибка при попытке найти заметку {slug} пользователя {author}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return 500, None

    if note is None:
        print(f'Не удалось найти заметку {slug} пользователя {author}')
        messages.error(
            request=request,
            message='Не удалось найти заметку',
        )
        return 404, None

    print(f'Заметка {slug} пользователя {author} найдена')
    return 200, note


def edit_note(request: Any, slug: str) -> (int, str):
    status, note = get_note(
        request=request,
        slug=slug,
    )
    if status != 200:
        return status, None

    print(f'Редактирование заметки {slug} с данными {request.POST}')
    status, note = edit_or_create_note(
        request=request,
        note=note,
    )

    if status == 200:
        print(f'Заметка {note} пользователя {request.user} изменена')
        messages.success(
            request=request,
            message='Заметка успешно изменена',
        )
    return status, note.slug


def create_note(request: Any) -> int:
    print(f'Cоздание заметки {request.POST} пользователем {request.user}')
    status, note = edit_or_create_note(
        request=request,
    )
    if status == 200:
        messages.success(
            request=request,
            message='Заметка успешно создана',
        )

    print(f'Заметка {note} пользователя {request.user} успешно создана')
    return status


def edit_or_create_note(request: Any, note: Note = None) -> (int, Note):
    data = request.POST
    form = NoteForm(data, note)
    if not form.is_valid():
        print(f'Невалидные данные {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400, None

    form.instance.author = request.user
    try:
        form.save()
    except Exception as exc:
        print(f'Возникла ошибка при сохранении изменений заметки {form.instance} пользователя {request.user}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return 500, None

    return 200, form.instance


def delete_note(request: Any, slug: str) -> int:
    status, note = get_note(
        request=request,
        slug=slug,
    )
    if status != 200:
        return status

    print(f'Удаление заметки {note} пользователя {request.user}')
    try:
        note.delete()
    except Exception as exc:
        print(f'Возникла ошибка при удалении заметки {note} пользователя {request.user}: {exc}')
        messages.error(
            request=request,
            message='Не удалось удалить заметку',
        )
        return 500

    print(f'Заметка {note} пользователя {request.user} успешно удалена')
    messages.success(
        request=request,
        message='Заметка успешно удалена',
    )
    return 200
