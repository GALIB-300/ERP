# A - Import Required Modules #
from django.contrib import admin
from django.conf import settings   
from .models import ResourceProfile, Resource

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

# D - ResourceProfile Admin #
@admin.register(ResourceProfile)
class ResourceProfileAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    ordering = ['user__username']

# E - Resource Admin #
@admin.register(Resource)
class ResourceAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['name_of_resource', 'unit', 'created_by', 'team', 'created_at']
    list_filter = ['unit', 'resource_group', 'team', 'created_by']  # ✅ lowercase
    search_fields = ['name_of_resource', 'unit', 'created_by__username']
    ordering = ['-created_at']

