from django.urls import path
from . import views

urlpatterns = [
    # Dashboard-Admins see all, team members see their own #
    path('dashboard/', views.project_dashboard, name='project_dashboard'),

    # ✏️ Edit project-Admins can edit all, team members only their own #
    path('dashboard/edit/<int:pk>/', views.edit_project, name='edit_project'),

    # 🗑️ Delete project-Admins can delete all, team members only their own #
    path('dashboard/delete/<int:pk>/', views.delete_project, name='delete_project'),
]
