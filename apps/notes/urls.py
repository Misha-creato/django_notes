from django.urls import path

from notes.views import (
    DetailView,
    EditView,
    DeleteView,
    CreateView,
    SearchView,
)


urlpatterns = [
    path(
        'create/',
        CreateView.as_view(),
        name='note_create',
    ),
    path(
        'edit/<str:slug>/',
        EditView.as_view(),
        name='note_edit',
    ),
    path(
        'delete/<str:slug>/',
        DeleteView.as_view(),
        name='note_delete',
    ),
    path(
        'search/',
        SearchView.as_view(),
        name='note_search',
    ),
    path(
        '<str:slug>/',
        DetailView.as_view(),
        name='note_detail',
    ),
]