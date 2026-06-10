from django.urls import path
from . import views

urlpatterns = [
    # Step-(A)-Team dashboard: team members manage their own requisition records #
    path('dashboard/', views.requisition_dashboard, name='requisition_dashboard'),

    # Step-(B)-Edit requisition entry (Team member can edit) #
    path('dashboard/edit/<int:pk>/', views.edit_requisition, name='edit_requisition'),

    # Step-(C)-Delete requisition entry (Team member can delete) #
    path('dashboard/delete/<int:pk>/', views.delete_requisition, name='delete_requisition'),

    # Step-(D)-Submit requisition for approval (Team only) #
    path('dashboard/submit/<int:pk>/', views.submit_requisition_for_approval, name='submit_requisition_for_approval'),

    # Step-(E)-Update requisition status (Admin only) #
path('dashboard/status/<int:pk>/', views.update_requisition_status, name='update_requisition_status'),

    # Step-(F)-Auto-fill API endpoint (Used by JavaScript) #
    path('dashboard/get_requisition_details/<int:pk>/', views.get_requisition_details, name='get_requisition_details'),
]
