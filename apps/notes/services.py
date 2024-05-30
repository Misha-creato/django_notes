from typing import Any

from django.contrib import messages
from django.urls import reverse

from config.settings import (
    SITE_PROTOCOL,
    SITE_DOMAIN,
)
from notes.forms import NoteForm
from notes.models import Note

from notifications.services import send_email_by_type

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
    author = request.user
    print(f'Редактирование заметки {slug} пользователя {author} с данными {request.POST}')
    status, note = get_note(
        request=request,
        slug=slug,
    )
    if status != 200:
        return status, None

    status, note = edit_or_create_note(
        request=request,
        note=note,
    )

    if status == 200:
        print(f'Заметка {note} пользователя {author} изменена')
        messages.success(
            request=request,
            message='Заметка успешно изменена',
        )
    return status, note.slug


def create_note(request: Any) -> int:
    author = request.user
    print(f'Cоздание заметки {request.POST} пользователем {author}')
    status, note = edit_or_create_note(
        request=request,
    )
    if status == 200:
        messages.success(
            request=request,
            message='Заметка успешно создана',
        )

    print(f'Заметка {note} пользователя {author} успешно создана')
    return status


def edit_or_create_note(request: Any, note: Note = None) -> (int, Note):
    data = request.POST
    form = NoteForm(data, instance=note)
    author = request.user
    if not form.is_valid():
        print(f'Невалидные данные при изменении '
              f'или создании заметки пользователя {author}: {form.errors}')
        set_form_messages(
            request=request,
            form=form,
        )
        return 400, None

    form.instance.author = author
    form.instance.notification_sent = False
    try:
        form.save()
    except Exception as exc:
        print(f'Возникла ошибка при сохранении изменений заметки {form.instance} пользователя {author}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return 500, None

    return 200, form.instance


def delete_note(request: Any, slug: str) -> int:
    author = request.user
    print(f'Удаление заметки {slug} пользователя {author}')
    status, note = get_note(
        request=request,
        slug=slug,
    )
    if status != 200:
        return status

    try:
        note.delete()
    except Exception as exc:
        print(f'Возникла ошибка при удалении заметки {note} пользователя {author}: {exc}')
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


def send_notification_email(note: Note):
    user = note.author
    print(f'Подготовка отправки письма-оповещения по заметке пользователю {user}')
    mail_data = get_note_mail_data(
        note=note,
        email_type='note_notification',
    )
    status = send_email_by_type(
        user=user,
        mail_data=mail_data,
        email_type='note_notification',
    )
    if status == 200:
        note.notification_sent = True
        try:
            note.save()
        except Exception as exc:
            print(f'Не удалось сохранить поле notification_sent заметки {note}: {exc}')
    return status


def get_note_mail_data(note: Note, email_type: str) -> dict:
    user = note.author
    print(f'Получение данных для формирования текста '
          f'письма {email_type} пользователю {user}')

    path = reverse('note_detail', args=(note.slug,))
    url = f'{SITE_PROTOCOL}://{SITE_DOMAIN}{path}'

    mail_data = {
        'note_title': note.title,
        'url': url,
    }

    print(f'Данные для формирования текста письма {email_type} '
          f'пользователю {user} получены: {mail_data}'
          )
    return mail_data


def search_notes(request: Any, page: int = 1) -> [Note]:
    page -= 1
    limit = 30
    query = request.GET.get('notes_query')
    print(f'Поиск по заголовку заметки {query}')
    try:
        notes = Note.objects.filter(
            author=request.user,
            title__icontains=query,
        )[page*limit:][:limit]
    except Exception as exc:
        print(f'Произошла ошибка при поиске заметки {query}: {exc}')
        return []
    print(f'Результат поиска по заголовку заметки {query}: {notes}')
    return notes


def load_notes(request: Any, search: bool = False) -> dict:
    page = int(request.GET.get('page'))

    if search:
        notes = search_notes(
            request=request,
            page=page,
        )
    else:
        notes = get_notes(
            request=request,
            page=page,
        )

    note_data = [{
        'title': note.title,
        'description': note.description,
        'slug': note.slug,
    } for note in notes]

    return {
        'notes': note_data,
    }


def get_notes(request: Any, page: int = 1) -> [Note]:
    page -= 1
    limit = 30
    print(f'Получение списка заметок пользователя {request.user}')
    try:
        notes = Note.objects.filter(
            author=request.user,
        )[page*limit:][:limit]
    except Exception as exc:
        print(f'Возникла ошибка при получении списка заметок пользователя {request.user}: {exc}')
        messages.error(
            request=request,
            message='Возникла ошибка',
        )
        return []
    print(f'Список заметок пользователя {request.user} получен')
    return notes
