# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # 📊 Dashboard - Admins see all, team members see/add their own #
    path('dashboard/', views.pt_dashboard, name='pt_dashboard'),

    # ✏️ Edit Proposal - Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_pt, name='edit_pt'),

    # 🗑️ Delete Proposal - Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_pt, name='delete_pt'),
]
