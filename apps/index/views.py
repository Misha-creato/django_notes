from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from notes.services import (
    get_notes,
    load_notes,
)


class IndexView(View):
    def get(self, request, *args, **kwargs):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = load_notes(
                request=request,
            )
            return JsonResponse(data)

        notes = get_notes(
            request=request,
        )
        context = {
            'notes': notes,
        }
        return render(
            request=request,
            template_name='index.html',
            context=context,
        )
