from django.contrib import admin
from configurations.models import Configuration
from solo.admin import SingletonModelAdmin


admin.site.register(Configuration, SingletonModelAdmin)
