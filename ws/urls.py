from django.urls import path
from . import views

urlpatterns = [
    path("ws/", views.ws_list, name="ws_list"),
    path("ws/add/", views.ws_add, name="ws_add"),
    path("ws/<int:pk>/edit/", views.edit_ws, name="edit_ws"),
    path("ws/<int:pk>/delete/", views.delete_ws, name="delete_ws"),
    path('ws/gantt-chart-data/', views.gantt_chart_data, name='ws_gantt_chart_data'),

]
