from django.urls import path
from . import views

urlpatterns = [
    # Dashboard-Admins see all, team members see their own #
    path('dashboard/', views.supplier_dashboard, name='supplier_dashboard'),

    # ✏️ Edit supplier-Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),

    # 🗑️ Delete supplier-Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),

    path('process/', views.supplier_process, name='supplier_process'),
]
