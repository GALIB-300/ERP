# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # Dashboard-Admins see all, team members see/add their own #
    path('dashboard/', views.stc_dashboard, name='stc_dashboard'),

    # ✏️ Edit STC-Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_stc, name='edit_stc'),

    # 🗑️ Delete STC-Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_stc, name='delete_stc'),
]
