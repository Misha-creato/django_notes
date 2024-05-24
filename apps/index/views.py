from django.shortcuts import render
from django.views import View

from index.services import get_notes


class IndexView(View):
    def get(self, request, *args, **kwargs):
        notes = get_notes(
            request=request,
        )
        context = {
            'notes': notes,
        }
        return render(
            request=request,
            template_name='index.html',
            context=context
        )
