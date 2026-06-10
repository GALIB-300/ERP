# A - Import Required Modules #
from django.contrib import admin
from django.conf import settings
from .models import SbProfile, Sb   # ✅ updated to sb-app

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

# D - SbProfile Admin #
@admin.register(SbProfile)
class SbProfileAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    ordering = ['user__username']

# E - Sb Admin #
@admin.register(Sb)
class SbAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['project_name_sb', 'supplier_name_sb', 'created_by', 'team', 'created_at']
    list_filter = ['team', 'created_by']
    search_fields = [
        'project_name_sb__project_name_po__name_of_project',    # ✅ nested lookup
        'supplier_name_sb__supplier_name_po__name_of_supplier', # ✅ nested lookup
        'created_by__username'
    ]
    ordering = ['-created_at']