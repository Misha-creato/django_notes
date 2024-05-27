from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from notes.services import get_notes


class IndexView(View): # TODO
    def get(self, request, *args, **kwargs):
        notes = get_notes(
            request=request,
        )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            page_number = request.GET.get('page')
            page_obj = notes.get_page(page_number)

            note_data = [{
                'title': note.title,
                'description': note.description,
                'slug': note.slug
            } for note in page_obj]

            return JsonResponse({'notes': note_data, 'has_next': page_obj.has_next()})

        context = {
            'notes': notes.get_page(1),
        }
        return render(
            request=request,
            template_name='index.html',
            context=context,
        )
