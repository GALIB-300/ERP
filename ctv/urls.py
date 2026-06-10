# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # 📊 Dashboard - Admins see all, team members see/add their own #
    path('dashboard/', views.ctv_dashboard, name='ctv_dashboard'),

    # ✏️ Edit CTV - Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_ctv, name='edit_ctv'),

    # 🗑️ Delete CTV - Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_ctv, name='delete_ctv'),
]