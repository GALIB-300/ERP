# A - Import Required Modules #
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User
from .models import CtvProfile, Ctv

# B - Django Admin Check #
def is_django_admin(user):
    return user.is_superuser or user.is_staff

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

# D - CtvProfile Admin #
@admin.register(CtvProfile)
class CtvProfileAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    ordering = ['user__username']

# E - Ctv Admin #
@admin.register(Ctv)
class CtvAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['client_name_ctv', 'description_work_ctv', 'created_by', 'team', 'created_at']
    list_filter = ['team', 'created_by']
    search_fields = ['client_name_ctv__client_name_pt', 'description_work_ctv', 'created_by__username']
    ordering = ['-created_at']