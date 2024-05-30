from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from notes.services import (
    get_note,
    edit_note,
    delete_note,
    create_note,
    search_notes,
    load_notes,
)


class DetailView(LoginRequiredMixin, View):
    def get(self, request, slug):
        status, note = get_note(
            request=request,
            slug=slug,
        )
        if status != 200:
            return redirect('index')
        context = {
            'note': note,
            'min_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        }
        return render(
            request=request,
            template_name='note_detail.html',
            context=context,
        )


class EditView(LoginRequiredMixin, View):
    def post(self, request, slug):
        status, slug = edit_note(
            request=request,
            slug=slug,
        )
        return redirect('note_detail', slug)


class CreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'min_date': timezone.now().strftime('%Y-%m-%dT%H:%M')
        }
        return render(
            request=request,
            template_name='note_create.html',
            context=context,
        )

    def post(self, request, *args, **kwargs):
        status = create_note(
            request=request,
        )
        if status != 200:
            return redirect('note_create')
        return redirect('index')


class DeleteView(LoginRequiredMixin, View):
    def post(self, request, slug):
        status = delete_note(
            request=request,
            slug=slug,
        )
        if status != 200:
            return redirect('detail', slug)
        return redirect('index')


class SearchView(View):
    def get(self, request, *args, **kwargs):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = load_notes(
                request=request,
                search=True,
            )
            return JsonResponse(data)

        notes = search_notes(
            request=request,
        )
        context = {
            'notes': notes,
        }
        return render(
            request=request,
            template_name='notes_search_results.html',
            context=context,
        )
