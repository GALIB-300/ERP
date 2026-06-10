from django.urls import path
from . import views

urlpatterns = [
    path("casting/", views.casting_list, name="casting_list"),
    path("casting/add/", views.casting_add, name="casting_add"),
    path("casting/<int:pk>/edit/", views.edit_casting, name="edit_casting"),
    path("casting/<int:pk>/delete/", views.delete_casting, name="delete_casting"),
]

