from django.contrib import admin

from solo.admin import SingletonModelAdmin

from notifications.forms import EmailTemplateForm
from notifications.models import (
    EmailTemplate,
    EmailConfiguration,
)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateForm
    list_display = [
        'email_type',
    ]


admin.site.register(EmailConfiguration, SingletonModelAdmin)
