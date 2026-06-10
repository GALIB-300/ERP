from django.urls import path
from . import views

app_name = 'construction'  # Namespace for reverse URL resolution

urlpatterns = [
    path('project-detailed/', views.construction_pd_list, name='construction_pd_list'),
]
