"""
inventory/admin.py
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AssetCategory, Asset, AssetTransfer,
    StockItem, StockTransaction,
    Ticket, TicketComment,
)


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'description']
    search_fields = ['name']


class AssetTransferInline(admin.TabularInline):
    model = AssetTransfer
    extra = 0
    readonly_fields = ['from_user', 'to_user', 'reason', 'status', 'created_at']
    can_delete = False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'amn_tag', 'name', 'category', 'brand',
        'status_badge', 'assigned_to', 'location', 'created_at',
    ]
    list_filter = ['status', 'category', 'brand']
    search_fields = ['amn_tag', 'name', 'brand', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AssetTransferInline]
    ordering = ['amn_tag']

    def status_badge(self, obj):
        colors = {
            'available': '#22c55e',
            'assigned': '#3b82f6',
            'maintenance': '#f59e0b',
            'retired': '#6b7280',
            'lost': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = ['asset', 'from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status']
    readonly_fields = ['created_at']


class StockTransactionInline(admin.TabularInline):
    model = StockTransaction
    extra = 0
    readonly_fields = [
        'transaction_type', 'quantity', 'quantity_before',
        'quantity_after', 'reason', 'performed_by', 'timestamp',
    ]
    can_delete = False
    max_num = 10
    ordering = ['-timestamp']


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'quantity_display',
        'alert_threshold', 'unit', 'location', 'is_active',
    ]
    list_filter = ['category', 'unit', 'is_active']
    search_fields = ['name', 'sku', 'supplier']
    readonly_fields = ['sku', 'created_at', 'updated_at']
    inlines = [StockTransactionInline]

    def quantity_display(self, obj):
        color = '#ef4444' if obj.quantity == 0 else '#f59e0b' if obj.is_low_stock else '#22c55e'
        return format_html(
            '<span style="color:{};font-weight:600">{} {}</span>',
            color, obj.quantity, obj.get_unit_display()
        )
    quantity_display.short_description = 'Quantité'


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'item', 'transaction_type', 'quantity',
        'quantity_before', 'quantity_after',
        'performed_by', 'timestamp',
    ]
    list_filter = ['transaction_type', 'timestamp']
    search_fields = ['item__name', 'reason', 'reference']
    readonly_fields = [
        'item', 'transaction_type', 'quantity', 'quantity_before',
        'quantity_after', 'reason', 'reference', 'performed_by', 'timestamp',
    ]
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 1
    readonly_fields = ['created_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'subject', 'submitted_by',
        'category', 'priority_badge', 'status_badge',
        'assigned_to', 'created_at',
    ]
    list_filter = ['status', 'priority', 'category']
    search_fields = ['ticket_number', 'subject', 'submitted_by__username']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']
    inlines = [TicketCommentInline]

    def priority_badge(self, obj):
        colors = {
            'low': '#6b7280',
            'medium': '#3b82f6',
            'high': '#f59e0b',
            'critical': '#ef4444',
        }
        color = colors.get(obj.priority, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px">{} {}</span>',
            color, obj.priority_icon, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priorité'

    def status_badge(self, obj):
        colors = {
            'open': '#ef4444',
            'in_progress': '#f59e0b',
            'waiting': '#6b7280',
            'resolved': '#22c55e',
            'closed': '#1f2937',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
