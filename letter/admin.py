# A - Import Required Modules #
from django.contrib import admin
from django.conf import settings
from .models import LetterProfile, Letter

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

# D - LetterProfile Admin #
@admin.register(LetterProfile)
class LetterProfileAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    ordering = ['user__username']

# E - Letter Admin #
@admin.register(Letter)
class LetterAdmin(DjangoAdminOnlyMixin, admin.ModelAdmin):
    list_display = [
        'client_name_letter',
        'wo_no_letter',
        'created_by',
        'team',
        'created_at',
    ]
    list_filter = ['team', 'created_by']
    search_fields = [
        'client_name_letter__client_name_cba__client_name_ctv__client_name_pt__name_of_client',
        'wo_no_letter__wo_no_cba',
        'created_by__username',
    ]
    ordering = ['-created_at']
