# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # Dashboard-Admins see all, team members see/add their own #
    path('dashboard/', views.rip_dashboard, name='rip_dashboard'),

    # ✏️ Edit RIP-Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_rip, name='edit_rip'),

    # 🗑️ Delete RIP-Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_rip, name='delete_rip'),

    # 🔎 Auto-Fill API (Used by JavaScript) #
    path('dashboard/get_rip_details/<int:pk>/', views.get_rip_details, name='get_rip_details'),
]