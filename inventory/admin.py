"""
Administration Django — Module Inventaire & Helpdesk.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from inventory.models import Asset, StockItem, StockTransaction, Ticket


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['amn_tag', 'brand', 'category', 'status_badge', 'assigned_to', 'purchase_date']
    list_filter = ['category', 'status']
    search_fields = ['amn_tag', 'brand', 'serial_number', 'assigned_to__username']
    autocomplete_fields = ['assigned_to']
    readonly_fields = ['created_at', 'updated_at', 'assigned_at']

    def status_badge(self, obj):
        colors = {
            'AVAILABLE': '#10b981',
            'ASSIGNED': '#3b82f6',
            'IN_REPAIR': '#f59e0b',
            'LOST': '#ef4444',
            'RETIRED': '#6b7280',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Statut')


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'alert_threshold', 'stock_indicator', 'unit', 'location']
    list_filter = ['location']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at', 'updated_at']

    def stock_indicator(self, obj):
        if obj.is_critical_stock:
            return format_html('<span style="color:#ef4444;font-weight:bold">🔴 Critique</span>')
        if obj.is_low_stock:
            return format_html('<span style="color:#f59e0b;font-weight:bold">🟠 Bas</span>')
        return format_html('<span style="color:#10b981">🟢 OK</span>')
    stock_indicator.short_description = _('Niveau')


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'item', 'transaction_type', 'quantity', 'quantity_before', 'quantity_after', 'performed_by']
    list_filter = ['transaction_type']
    search_fields = ['item__name', 'performed_by__username', 'reason']
    readonly_fields = ['timestamp', 'item', 'transaction_type', 'quantity', 'quantity_before', 'quantity_after', 'performed_by', 'reason']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'priority_badge', 'status', 'submitted_by', 'assigned_to', 'created_at']
    list_filter = ['priority', 'status']
    search_fields = ['subject', 'description', 'submitted_by__username']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    autocomplete_fields = ['submitted_by', 'assigned_to', 'asset']

    def priority_badge(self, obj):
        colors = {
            'LOW': '#6b7280',
            'MEDIUM': '#3b82f6',
            'HIGH': '#f59e0b',
            'SOS': '#ef4444',
        }
        color = colors.get(obj.priority, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:bold">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = _('Priorité')
