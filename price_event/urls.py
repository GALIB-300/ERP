# A - Import Required Modules #
from django.urls import path
from . import views

# B - URL Patterns #
urlpatterns = [
    # Dashboard (list + create)
    path('dashboard/', views.price_event_dashboard, name='price_event_dashboard'),

    # Update existing event
    path('update/<int:pk>/', views.price_event_update, name='price_event_update'),

    # Delete existing event
    path('delete/<int:pk>/', views.price_event_delete, name='price_event_delete'),
    path('process/', views.price_event_process, name='price_event_process'),

]

