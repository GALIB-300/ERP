# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # 📊 Dashboard - Admins see all, team members see/add their own #
    path('dashboard/', views.sb_dashboard, name='sb_dashboard'),

    # ✏️ Edit SB - Team members edit only their own (Admins cannot edit) #
    path('dashboard/edit/<int:pk>/', views.edit_sb, name='edit_sb'),

    # 🗑️ Delete SB - Team members delete only their own (Admins cannot delete) #
    path('dashboard/delete/<int:pk>/', views.delete_sb, name='delete_sb'),

    # 🔎 Auto-fill-Unit-(Pull from-po-app) #
    path('dashboard/get_sb_unit/<int:pk>/', views.get_sb_unit, name='get_sb_unit'),

    # 📦 Auto-fill-Quantity-(Pull from-po-app) #
    path('dashboard/get_sb_quantity/', views.get_sb_quantity, name='get_sb_quantity'),

    # 💰 Auto-fill-Price-(Pull from-po-app) #
    path('dashboard/get_sb_price/', views.get_sb_price, name='get_sb_price'),

]
