from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from notes.models import Note


def validate_notify_date(value):
    min_date = timezone.now()
    if value < min_date:
        raise ValidationError(
            'Дата и время оповещения не могут быть в прошлом.'
        )


class NoteForm(forms.ModelForm):
    notify_at = forms.DateTimeField(
        validators=[validate_notify_date]
    )

    class Meta:
        model = Note
        fields = [
            'title',
            'description',
            'notify_at',
        ]
