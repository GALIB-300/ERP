# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # Dashboard-Admins see all, team members see/add their own #
    path('dashboard/', views.rbp_dashboard, name='rbp_dashboard'),

    # ✏️ Edit RBP-Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_rbp, name='edit_rbp'),

    # 🗑️ Delete RBP-Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_rbp, name='delete_rbp'),

    # 🔎 Auto-Fill API (Used by JavaScript) #
    path('dashboard/get_rbp_details/<int:pk>/', views.get_rbp_details, name='get_rbp_details'),
]

