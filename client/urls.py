from django.urls import path
from . import views

urlpatterns = [
    # Dashboard-Admins see all, team members see their own #
    path('dashboard/', views.client_dashboard, name='client_dashboard'),

    # ✏️ Edit client-Team members only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_client, name='edit_client'),

    # 🗑️ Delete client-Team members only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_client, name='delete_client'),
]
