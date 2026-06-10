# A - Import Required Modules #
from django.contrib import admin
from .models import PriceEventProfile, ResourcePriceEvent

# B - PriceEventProfile Admin #
@admin.register(PriceEventProfile)
class PriceEventProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    ordering = ['user__username']

# C - ResourcePriceEvent Admin #
@admin.register(ResourcePriceEvent)
class ResourcePriceEventAdmin(admin.ModelAdmin):
    list_display = [
        'resource_name',
        'supplier_name',
        'base_price',
        'increase_decrease_price',
        'actual_price',
        'effective_from',
        'effective_to',
        'created_by',
        'updated_by',
        'created_at',
        'updated_at',
    ]
    list_filter = ['supplier_name', 'resource_name', 'created_by']
    search_fields = ['resource_name', 'supplier_name', 'created_by__username']
    ordering = ['-effective_from']
