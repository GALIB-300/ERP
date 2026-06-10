# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # Dashboard-Admins see all, team members see/add their own #
    path('dashboard/', views.pr_dashboard, name='pr_dashboard'),

    # ✏️ Edit PR-Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_pr, name='edit_pr'),

    # 🗑️ Delete PR-Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_pr, name='delete_pr'),

    # 🔎 Auto-Fill API (Used by JavaScript) #
    path('dashboard/get_pr_details/<int:pk>/', views.get_pr_details, name='get_pr_details'),

    # Print based-URL #
    path("print/", views.print_dashboard, name="print_dashboard"),
]
