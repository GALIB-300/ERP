from django.urls import path
from . import views
urlpatterns = [
    path('dashboard/', views.customerdetailed_dashboard, name='customerdetailed_dashboard'),
    path('dashboard/edit/<int:pk>/', views.edit_customerdetailed, name='edit_customerdetailed'),
    path('dashboard/delete/<int:pk>/', views.Customerdetailed_delete, name='delete_customerdetailed'),
]
