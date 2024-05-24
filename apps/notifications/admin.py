from django.contrib import admin

from notifications.forms import EmailTemplateForm
from notifications.models import EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateForm
    list_display = [
        'email_type',
    ]
