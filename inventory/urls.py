"""
URLs — Module Inventaire & Helpdesk.
AMN Employee Hub.
"""

from django.urls import path

from inventory import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard Warehouse (managers)
    path('', views.WarehouseDashboardView.as_view(), name='dashboard'),

    # Vue employé : Mon Bureau Digital
    path('my-assets/', views.MyAssetsView.as_view(), name='my_assets'),

    # Transfert P2P
    path('assets/<int:asset_id>/transfer/', views.transfer_asset, name='transfer_asset'),

    # Helpdesk — Ticket flow
    path('helpdesk/', views.HelpdeskView.as_view(), name='helpdesk'),
    path('helpdesk/<int:ticket_id>/status/', views.update_ticket_status, name='update_ticket_status'),

    # Stock updates (AJAX)
    path('stock/<int:item_id>/update/', views.update_stock, name='update_stock'),
    path('stock/<int:item_id>/qr/', views.stock_item_by_qr, name='stock_qr'),

    # Tutoriel : Marquer comme vu (AJAX)
    path('tutorial/seen/', views.mark_tutorial_seen, name='tutorial_seen'),
]
