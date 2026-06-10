# A - Import Required Modules #
from django.contrib import admin
from django.conf import settings   
from .models import RbpProfile, Rbp

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser or user.is_staff

# Define the admin email (either hardcoded or from settings) #
DJANGO_ADMIN_EMAIL = getattr(settings, "DJANGO_ADMIN_EMAIL", "admin@example.com")

# C - Mixin: Restrict Admin Access to Django Admin #
class DjangoAdminOnlyMixin:
    def has_module_permission(self, request):
        return request.user.email == DJANGO_ADMIN_EMAIL

    def has_view_permission(self, request, obj=None):
        return request.user.email == DJANGO_ADMIN_EMAIL

    def has_change_permission(self, request, obj=None):
        return request.user.email == DJANGO_ADMIN_EMAIL

    def has_delete_permission(self, request, obj=None):
        return request.user.email == DJANGO_ADMIN_EMAIL

# D - RbpProfile Admin #
@admin.register(RbpProfile)
class RbpProfileAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    ordering = ['user__username']

# E - Rbp Admin #
@admin.register(Rbp)
class RbpAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['project_name_rbp', 'resource_name_rbp', 'created_by', 'team', 'created_at']
    list_filter = ['team', 'created_by']  
    search_fields = ['project_name_rbp__name_of_project', 'resource_name_rbp__name_of_resource', 'created_by__username']
    ordering = ['-created_at']
