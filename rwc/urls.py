from django.urls import path
from . import views

urlpatterns = [
    # 📊 Dashboard (form + table)
    path('dashboard/', views.rwc_dashboard, name='rwc_dashboard'),

    # ✏️ Edit requisition (team members edit only their own, admins cannot edit)
    path('dashboard/edit/<int:pk>/', views.edit_rwc, name='edit_rwc'),

    # 🗑️ Delete requisition (team members delete only their own, admins cannot delete)
    path('dashboard/delete/<int:pk>/', views.delete_rwc, name='delete_rwc'),

    path('rwc/<int:pk>/print/', views.rwc_print_view, name='rwc_print'),
]
