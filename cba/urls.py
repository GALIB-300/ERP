# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # 📊 Dashboard - Admins see all, team members see/add their own #
    path('dashboard/', views.cba_dashboard, name='cba_dashboard'),

    # ✏️ Edit CBA - Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_cba, name='edit_cba'),

    # 🗑️ Delete CBA - Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_cba, name='delete_cba'),
]
