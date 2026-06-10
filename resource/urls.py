from django.urls import path
from . import views

urlpatterns = [
    # Dashboard-Admins see all, team members see their own #
    path('dashboard/', views.resource_dashboard, name='resource_dashboard'),

    # ✏️ Edit resource-Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_resource, name='edit_resource'),

    # 🗑️ Delete resource-Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_resource, name='delete_resource'),

    # 📋 List-only page (table only, no form)
    path('resources/list/', views.resource_list_only, name='resource_list_only'),

]
