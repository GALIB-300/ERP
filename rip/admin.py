# A - Import Required Modules #
from django.contrib import admin
from django.conf import settings
from .models import RipProfile, Rip

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_staff or user.is_superuser

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

# D - RipProfile Admin #
@admin.register(RipProfile)
class RipProfileAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    ordering = ['user__username']

# E - Rip Admin #
@admin.register(Rip)
class RipAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['project_name_rip', 'resource_name_rip', 'created_by', 'team', 'created_at']
    list_filter = ['team', 'created_by']
    search_fields = ['project_name_rip__project_name_rbp', 'resource_name_rip__resource_name_rbp', 'created_by__username']
    ordering = ['-created_at']

