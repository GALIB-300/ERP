from django.urls import path
from . import views

urlpatterns = [
    # 📊 Dashboard (form + table)
    path('dashboard/', views.company_dashboard, name='company_dashboard'),

    # ✏️ Edit company (team members edit only their own, admins cannot edit)
    path('dashboard/edit/<int:pk>/', views.edit_company, name='edit_company'),

    # 🗑️ Delete company (team members delete only their own, admins cannot delete)
    path('dashboard/delete/<int:pk>/', views.delete_company, name='delete_company'),
]
