from django.urls import path
from . import views

urlpatterns = [
    # Dashboard - Admins see all, team members see their own
    path('dashboard/', views.proposal_dashboard, name='proposal_dashboard'),

    # ✏️ Edit Proposal - Team members only their own (Admins cannot edit)
    path('dashboard/edit/<int:pk>/', views.edit_proposal, name='edit_proposal'),

    # 🗑️ Delete Proposal - Team members only their own (Admins cannot delete)
    path('dashboard/delete/<int:pk>/', views.delete_proposal, name='delete_proposal'),
]

