# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # Dashboard-Admins see all, team members see/add their own #
    path('dashboard/', views.po_dashboard, name='po_dashboard'),

    # ✏️ Edit PO-Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_po, name='edit_po'),

    # 🗑️ Delete PO-Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_po, name='delete_po'),

    # 🔎 Auto-Fill API (Used by JavaScript) #
    path('dashboard/get_po_details/<int:pk>/', views.get_po_details, name='get_po_details'),

    # Print based-URL #
    path("print-po/", views.print_po_dashboard, name="print_po_dashboard"),

]
