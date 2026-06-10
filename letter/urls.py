from django.urls import path
from . import views

urlpatterns = [
    path("letters/", views.letter_list, name="letter_list"),
    path("letters/add/", views.letter_add, name="letter_add"),
    path("letters/<int:pk>/edit/", views.edit_letter, name="edit_letter"),
    path("letters/<int:pk>/delete/", views.delete_letter, name="delete_letter"),
    path("print-letter/", views.letter_print, name="letter_print"),
]
