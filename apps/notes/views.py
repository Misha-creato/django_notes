from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from notes.services import get_note, edit_note, delete_note, create_note


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
        return render(
            request=request,
            template_name='note_create.html',
        )

    def post(self, request, *args, **kwargs):
        status, slug = create_note(
            request=request,
        )
        if status != 200:
            return redirect('note_create')
        return redirect('note_detail', slug)


class DeleteView(LoginRequiredMixin, View):
    def post(self, request, slug):
        status = delete_note(
            request=request,
            slug=slug,
        )
        if status != 200:
            return redirect('detail', slug)
        return redirect('index')
