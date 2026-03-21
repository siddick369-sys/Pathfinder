"""
Vues — Module 3 Inventaire, Stock Global & Helpdesk.
AMN Employee Hub.

Logique tutoriel interactif intégrée : has_seen_inventory_tutorial.
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_POST

from inventory.forms import (
    AssetForm,
    AssetTransferForm,
    StockItemForm,
    StockUpdateForm,
    TicketForm,
)
from inventory.models import (
    Asset,
    StockItem,
    StockTransaction,
    Ticket,
    TicketPriority,
    TicketStatus,
    TransactionType,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _check_tutorial(request):
    """
    Retourne True si le tutoriel doit être affiché pour cet utilisateur.
    Met à jour has_seen_inventory_tutorial si l'utilisateur l'a déjà vu.
    """
    user = request.user
    return not getattr(user, 'has_seen_inventory_tutorial', True)


# ─────────────────────────────────────────────────────────────────────────────
# API TUTORIEL : Marquer comme vu (AJAX)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def mark_tutorial_seen(request):
    """Endpoint AJAX pour enregistrer que l'utilisateur a vu le tutoriel."""
    try:
        request.user.has_seen_inventory_tutorial = True
        request.user.save(update_fields=['has_seen_inventory_tutorial'])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f'Erreur mark_tutorial_seen: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ─────────────────────────────────────────────────────────────────────────────
# VUE PRINCIPALE : Dashboard Warehouse (Managers)
# ─────────────────────────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class WarehouseDashboardView(View):
    """
    Tableau de bord Warehouse pour les responsables stock.
    Onglet 1 : Stock Global (consommables).
    Onglet 2 : Équipements individuels (Assets).
    """
    template_name = 'inventory/dashboard.html'

    def get(self, request):
        if not request.user.is_staff:
            return redirect('inventory:my_assets')

        # Stock global
        stock_items = StockItem.objects.all().order_by('name')
        low_stock_items = [i for i in stock_items if i.is_low_stock]
        critical_stock_items = [i for i in stock_items if i.is_critical_stock]

        # Équipements
        assets = Asset.objects.select_related('assigned_to').all()
        available_assets = assets.filter(status='AVAILABLE')
        assigned_assets = assets.filter(status='ASSIGNED')

        # Tickets ouverts
        open_tickets = Ticket.objects.filter(
            status__in=[TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
        ).select_related('submitted_by').order_by('-created_at')
        sos_tickets = open_tickets.filter(priority=TicketPriority.CRITICAL)

        # Formulaires
        stock_update_form = StockUpdateForm()
        stock_item_form = StockItemForm()
        asset_form = AssetForm()

        context = {
            'stock_items': stock_items,
            'low_stock_items': low_stock_items,
            'critical_stock_items': critical_stock_items,
            'assets': assets,
            'available_assets': available_assets,
            'assigned_assets': assigned_assets,
            'open_tickets': open_tickets,
            'sos_tickets': sos_tickets,
            'stock_update_form': stock_update_form,
            'stock_item_form': stock_item_form,
            'asset_form': asset_form,
            'show_tutorial': _check_tutorial(request),
            'active_tab': request.GET.get('tab', 'stock'),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Traite la création d'un article de stock ou d'un équipement."""
        if not request.user.is_staff:
            return JsonResponse({'error': 'Forbidden'}, status=403)

        action = request.POST.get('action')

        if action == 'add_stock_item':
            form = StockItemForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _('Article de stock ajouté avec succès.'))
            else:
                messages.error(request, _('Erreur dans le formulaire.'))

        elif action == 'add_asset':
            form = AssetForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _('Équipement ajouté avec succès.'))
            else:
                messages.error(request, _('Erreur dans le formulaire.'))

        return redirect('inventory:dashboard')


# ─────────────────────────────────────────────────────────────────────────────
# MISE À JOUR STOCK : Boutons + et -
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def update_stock(request, item_id):
    """
    Met à jour la quantité d'un article de stock.
    Crée un StockTransaction immuable (audit trail).
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    item = get_object_or_404(StockItem, pk=item_id)
    form = StockUpdateForm(request.POST)

    if not form.is_valid():
        return JsonResponse({'error': str(form.errors)}, status=400)

    qty = form.cleaned_data['quantity']
    txn_type = form.cleaned_data['transaction_type']
    reason = form.cleaned_data.get('reason', '')

    with transaction.atomic():
        qty_before = item.quantity

        if txn_type == TransactionType.IN:
            item.quantity += qty
        elif txn_type == TransactionType.OUT:
            if item.quantity < qty:
                return JsonResponse(
                    {'error': _('Stock insuffisant.')},
                    status=400
                )
            item.quantity -= qty

        item.save(update_fields=['quantity', 'updated_at'])

        StockTransaction.objects.create(
            item=item,
            transaction_type=txn_type,
            quantity=qty,
            quantity_before=qty_before,
            quantity_after=item.quantity,
            performed_by=request.user,
            reason=reason,
        )

    return JsonResponse({
        'status': 'ok',
        'new_quantity': item.quantity,
        'stock_level': item.stock_level,
        'item_name': item.name,
    })


# ─────────────────────────────────────────────────────────────────────────────
# VUE EMPLOYÉ : Mon Bureau Digital
# ─────────────────────────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class MyAssetsView(View):
    """
    Vue "Mon Bureau Digital" pour les employés.
    Affiche les équipements assignés et les tickets en cours.
    """
    template_name = 'inventory/my_assets.html'

    def get(self, request):
        my_assets = Asset.objects.filter(assigned_to=request.user).select_related()
        my_tickets = Ticket.objects.filter(submitted_by=request.user).order_by('-created_at')
        transfer_form = AssetTransferForm(current_user=request.user)

        context = {
            'my_assets': my_assets,
            'my_tickets': my_tickets,
            'transfer_form': transfer_form,
            'show_tutorial': _check_tutorial(request),
            'open_tickets_count': my_tickets.filter(
                status__in=[TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
            ).count(),
        }
        return render(request, self.template_name, context)


# ─────────────────────────────────────────────────────────────────────────────
# TRANSFERT P2P
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def transfer_asset(request, asset_id):
    """Transfère un équipement à un autre employé (P2P)."""
    asset = get_object_or_404(Asset, pk=asset_id, assigned_to=request.user)
    form = AssetTransferForm(request.POST, current_user=request.user)

    if form.is_valid():
        new_owner = form.cleaned_data['new_owner']
        asset.assign_to(new_owner)
        messages.success(
            request,
            _(f'Équipement {asset.amn_tag} transféré à {new_owner.get_full_name()}.')
        )
    else:
        messages.error(request, _('Erreur dans le formulaire de transfert.'))

    return redirect('inventory:my_assets')


# ─────────────────────────────────────────────────────────────────────────────
# HELPDESK : Ticket Flow
# ─────────────────────────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class HelpdeskView(View):
    """Vue de création et suivi de tickets Helpdesk."""
    template_name = 'inventory/helpdesk.html'

    def get(self, request):
        form = TicketForm(user=request.user)
        my_tickets = Ticket.objects.filter(submitted_by=request.user).order_by('-created_at')

        # Manager : voit tous les tickets
        all_tickets = None
        if request.user.is_staff:
            all_tickets = Ticket.objects.select_related('submitted_by', 'assigned_to').order_by('-created_at')

        context = {
            'form': form,
            'my_tickets': my_tickets,
            'all_tickets': all_tickets,
            'show_tutorial': _check_tutorial(request),
            'TicketStatus': TicketStatus,
            'TicketPriority': TicketPriority,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = TicketForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.submitted_by = request.user
            ticket.save()
            messages.success(
                request,
                _('Votre ticket a été soumis avec succès. Notre équipe IT reviendra vers vous rapidement.')
            )
            return redirect('inventory:helpdesk')

        my_tickets = Ticket.objects.filter(submitted_by=request.user).order_by('-created_at')
        context = {
            'form': form,
            'my_tickets': my_tickets,
            'show_tutorial': _check_tutorial(request),
            'TicketStatus': TicketStatus,
            'TicketPriority': TicketPriority,
        }
        return render(request, self.template_name, context)


# ─────────────────────────────────────────────────────────────────────────────
# MANAGER : Mettre à jour le statut d'un ticket
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def update_ticket_status(request, ticket_id):
    """Permet aux managers de changer le statut d'un ticket."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    ticket = get_object_or_404(Ticket, pk=ticket_id)
    new_status = request.POST.get('status')

    if new_status not in dict(TicketStatus.choices):
        return JsonResponse({'error': 'Invalid status'}, status=400)

    ticket.status = new_status
    if new_status == TicketStatus.RESOLVED:
        ticket.resolved_at = timezone.now()
        ticket.assigned_to = request.user
    ticket.save(update_fields=['status', 'resolved_at', 'assigned_to'])

    return JsonResponse({
        'status': 'ok',
        'new_status': ticket.get_status_display(),
        'ticket_id': ticket.pk,
    })


# ─────────────────────────────────────────────────────────────────────────────
# QR CODE SCANNER API
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def stock_item_by_qr(request, item_id):
    """Retourne les informations d'un article de stock via son QR code (JSON)."""
    try:
        item = StockItem.objects.get(pk=item_id)
        return JsonResponse({
            'id': item.pk,
            'name': item.name,
            'quantity': item.quantity,
            'unit': item.unit,
            'stock_level': item.stock_level,
            'location': item.location,
            'alert_threshold': item.alert_threshold,
        })
    except StockItem.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
