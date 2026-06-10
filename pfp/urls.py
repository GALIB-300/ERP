from django.urls import path
from . import views

urlpatterns = [
    # Dashboard-Admins see all, team members see their own #
    path('dashboard/', views.pfp_dashboard, name='pfp_dashboard'),

    # ✏️ Edit PFP-Team members only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_pfp, name='edit_pfp'),

    # 🗑️ Delete PFP-Team members only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_pfp, name='delete_pfp'),
]
