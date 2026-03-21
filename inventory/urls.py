"""
inventory/urls.py
"""
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # ── Index (redirige selon le rôle) ──
    path('', views.inventory_index, name='index'),

    # ── Manager : Dashboard Warehouse ──
    path('warehouse/', views.warehouse_dashboard, name='warehouse_dashboard'),

    # ── Stock Global ──
    path('stock/nouveau/', views.stock_item_create, name='stock_create'),
    path('stock/<int:pk>/modifier/', views.stock_item_edit, name='stock_edit'),
    path('stock/<int:pk>/ajuster/', views.stock_adjust, name='stock_adjust'),
    path('stock/<int:pk>/transactions/', views.stock_transactions, name='stock_transactions'),

    # ── Actifs individuels ──
    path('actifs/nouveau/', views.asset_create, name='asset_create'),
    path('actifs/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('actifs/<int:pk>/modifier/', views.asset_edit, name='asset_edit'),
    path('actifs/<int:asset_pk>/transfert/', views.request_transfer, name='request_transfer'),

    # ── Employé : Mon Bureau Digital ──
    path('mes-actifs/', views.my_assets, name='my_assets'),

    # ── Helpdesk ──
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/nouveau/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),

    # ── Tutoriel ──
    path('tutoriel/vu/', views.mark_tutorial_seen, name='mark_tutorial_seen'),

    # ── QR Code ──
    path('qr-scan/', views.qr_lookup, name='qr_lookup'),
]
