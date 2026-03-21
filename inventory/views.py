"""
inventory/views.py
Module 3 AMN Employee Hub — Gestion d'Actifs, Stock Global & Helpdesk
"""
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum

from .models import (
    Asset, AssetCategory, AssetTransfer,
    StockItem, StockTransaction,
    Ticket, TicketComment,
)
from .forms import (
    AssetForm, StockItemForm, StockAdjustForm,
    TicketForm, TicketStatusForm, TicketCommentForm,
    AssetTransferForm,
)


# ──────────────────────────────────────────────
# TUTORIEL : logique has_seen_inventory_tutorial
# ──────────────────────────────────────────────

def _should_show_tutorial(user):
    """Retourne True si l'utilisateur n'a pas encore vu le tutoriel."""
    return not getattr(user, 'has_seen_inventory_tutorial', True)


@login_required
@require_POST
def mark_tutorial_seen(request):
    """AJAX — Marque le tutoriel comme vu pour l'utilisateur."""
    request.user.has_seen_inventory_tutorial = True
    request.user.save(update_fields=['has_seen_inventory_tutorial'])
    return JsonResponse({'status': 'ok'})


# ──────────────────────────────────────────────
# INDEX DU MODULE
# ──────────────────────────────────────────────

@login_required
def inventory_index(request):
    """Page d'accueil du module inventaire — redirige selon le rôle."""
    if request.user.is_staff:
        return redirect('inventory:warehouse_dashboard')
    return redirect('inventory:my_assets')


# ──────────────────────────────────────────────
# MANAGER — TABLEAU DE BORD WAREHOUSE
# ──────────────────────────────────────────────

@login_required
def warehouse_dashboard(request):
    """
    Dashboard responsable stock avec deux onglets :
    - Onglet 1 : Actifs individuels
    - Onglet 2 : Stock consommables
    """
    # Stats globales
    total_assets = Asset.objects.count()
    assigned_assets = Asset.objects.filter(status='assigned').count()
    maintenance_assets = Asset.objects.filter(status='maintenance').count()

    total_stock_items = StockItem.objects.filter(is_active=True).count()
    low_stock_items = [
        item for item in StockItem.objects.filter(is_active=True)
        if item.is_low_stock
    ]
    critical_stock_items = [i for i in low_stock_items if i.quantity == 0]

    open_tickets = Ticket.objects.filter(
        status__in=['open', 'in_progress']
    ).count()
    sos_tickets = Ticket.objects.filter(
        priority='critical', status__in=['open', 'in_progress']
    ).count()

    # Assets list
    assets_qs = Asset.objects.select_related('category', 'assigned_to').order_by('amn_tag')
    asset_search = request.GET.get('asset_q', '')
    if asset_search:
        assets_qs = assets_qs.filter(
            Q(amn_tag__icontains=asset_search) |
            Q(name__icontains=asset_search) |
            Q(brand__icontains=asset_search)
        )
    assets_paginator = Paginator(assets_qs, 20)
    assets_page = assets_paginator.get_page(request.GET.get('asset_page', 1))

    # Stock list
    stock_qs = StockItem.objects.filter(is_active=True).select_related('category').order_by('name')
    stock_search = request.GET.get('stock_q', '')
    if stock_search:
        stock_qs = stock_qs.filter(
            Q(name__icontains=stock_search) |
            Q(sku__icontains=stock_search)
        )
    stock_paginator = Paginator(stock_qs, 20)
    stock_page = stock_paginator.get_page(request.GET.get('stock_page', 1))

    # Transactions récentes
    recent_transactions = StockTransaction.objects.select_related(
        'item', 'performed_by'
    ).order_by('-timestamp')[:10]

    # Tickets récents
    recent_tickets = Ticket.objects.select_related(
        'submitted_by', 'assigned_to'
    ).order_by('-created_at')[:5]

    context = {
        'active_tab': request.GET.get('tab', 'stock'),
        # Stats
        'total_assets': total_assets,
        'assigned_assets': assigned_assets,
        'maintenance_assets': maintenance_assets,
        'total_stock_items': total_stock_items,
        'low_stock_items': low_stock_items,
        'critical_stock_items': critical_stock_items,
        'open_tickets': open_tickets,
        'sos_tickets': sos_tickets,
        # Listes
        'assets_page': assets_page,
        'stock_page': stock_page,
        'recent_transactions': recent_transactions,
        'recent_tickets': recent_tickets,
        # Filtres
        'asset_search': asset_search,
        'stock_search': stock_search,
        # Tutoriel
        'show_tutorial': _should_show_tutorial(request.user),
    }
    return render(request, 'inventory/warehouse_dashboard.html', context)


# ──────────────────────────────────────────────
# STOCK — CRUD & AJUSTEMENTS
# ──────────────────────────────────────────────

@login_required
def stock_item_create(request):
    """Créer un nouvel article en stock."""
    if not request.user.is_staff:
        messages.error(request, _('Accès refusé.'))
        return redirect('inventory:my_assets')

    form = StockItemForm(request.POST or None)
    if form.is_valid():
        item = form.save()
        messages.success(request, _(f'Article "{item.name}" créé avec succès.'))
        return redirect('inventory:warehouse_dashboard')

    return render(request, 'inventory/stock_item_form.html', {
        'form': form,
        'title': _('Nouvel article en stock'),
        'show_tutorial': _should_show_tutorial(request.user),
    })


@login_required
def stock_item_edit(request, pk):
    """Éditer un article en stock."""
    if not request.user.is_staff:
        messages.error(request, _('Accès refusé.'))
        return redirect('inventory:my_assets')

    item = get_object_or_404(StockItem, pk=pk)
    form = StockItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, _(f'Article "{item.name}" mis à jour.'))
        return redirect('inventory:warehouse_dashboard')

    return render(request, 'inventory/stock_item_form.html', {
        'form': form,
        'item': item,
        'title': _(f'Modifier — {item.name}'),
        'show_tutorial': _should_show_tutorial(request.user),
    })


@login_required
@require_POST
def stock_adjust(request, pk):
    """
    AJAX ou POST — Ajustement rapide du stock (boutons +/-).
    Crée une StockTransaction immuable (Audit Trail).
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    item = get_object_or_404(StockItem, pk=pk)
    form = StockAdjustForm(request.POST)

    if form.is_valid():
        direction = form.cleaned_data['direction']
        qty = form.cleaned_data['quantity']
        reason = form.cleaned_data.get('reason', '')
        reference = form.cleaned_data.get('reference', '')

        qty_before = item.quantity

        if direction == 'in':
            item.quantity += qty
            delta = qty
            item.last_restock_date = timezone.now().date()
        elif direction in ('out', 'loss'):
            if item.quantity < qty:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': _('Stock insuffisant'),
                        'available': item.quantity,
                    }, status=400)
                messages.error(request, _('Quantité insuffisante en stock.'))
                return redirect('inventory:warehouse_dashboard')
            item.quantity -= qty
            delta = -qty
        else:  # adjust
            delta = qty - item.quantity
            item.quantity = qty

        item.save(update_fields=['quantity', 'last_restock_date'] if direction == 'in' else ['quantity'])

        # Audit Trail immuable
        transaction = StockTransaction.objects.create(
            item=item,
            transaction_type=direction,
            quantity=delta,
            quantity_before=qty_before,
            quantity_after=item.quantity,
            reason=reason,
            reference=reference,
            performed_by=request.user,
        )

        # Déclenche l'alerte Celery si stock bas
        if item.is_low_stock:
            from .tasks import check_low_stock
            check_low_stock.apply_async(countdown=5)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            badge_color, badge_icon = item.stock_badge
            return JsonResponse({
                'status': 'ok',
                'new_quantity': item.quantity,
                'stock_status': item.stock_status,
                'badge_color': badge_color,
                'badge_icon': badge_icon,
                'transaction_id': transaction.pk,
            })

        messages.success(request, _(f'Stock de "{item.name}" mis à jour : {item.quantity} {item.get_unit_display()}.'))
        return redirect('inventory:warehouse_dashboard')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': str(form.errors)}, status=400)

    messages.error(request, _('Données invalides.'))
    return redirect('inventory:warehouse_dashboard')


@login_required
def stock_transactions(request, pk):
    """Historique des mouvements d'un article (Audit Trail)."""
    item = get_object_or_404(StockItem, pk=pk)
    transactions = item.transactions.select_related('performed_by').order_by('-timestamp')
    paginator = Paginator(transactions, 30)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'inventory/stock_transactions.html', {
        'item': item,
        'page': page,
        'show_tutorial': _should_show_tutorial(request.user),
    })


# ──────────────────────────────────────────────
# ASSETS — CRUD & TRANSFERTS
# ──────────────────────────────────────────────

@login_required
def asset_create(request):
    """Créer un nouvel actif."""
    if not request.user.is_staff:
        messages.error(request, _('Accès refusé.'))
        return redirect('inventory:my_assets')

    form = AssetForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        asset = form.save()
        if asset.assigned_to:
            asset.status = 'assigned'
            asset.assigned_at = timezone.now()
            asset.save(update_fields=['status', 'assigned_at'])
        messages.success(request, _(f'Actif "{asset.amn_tag}" créé.'))
        return redirect('inventory:warehouse_dashboard')

    return render(request, 'inventory/asset_form.html', {
        'form': form,
        'title': _('Nouvel actif'),
        'show_tutorial': _should_show_tutorial(request.user),
    })


@login_required
def asset_edit(request, pk):
    """Éditer un actif."""
    if not request.user.is_staff:
        messages.error(request, _('Accès refusé.'))
        return redirect('inventory:my_assets')

    asset = get_object_or_404(Asset, pk=pk)
    form = AssetForm(request.POST or None, request.FILES or None, instance=asset)
    if form.is_valid():
        form.save()
        messages.success(request, _(f'Actif "{asset.amn_tag}" mis à jour.'))
        return redirect('inventory:warehouse_dashboard')

    return render(request, 'inventory/asset_form.html', {
        'form': form,
        'asset': asset,
        'title': _(f'Modifier — {asset.amn_tag}'),
        'show_tutorial': _should_show_tutorial(request.user),
    })


@login_required
def asset_detail(request, pk):
    """Détail complet d'un actif."""
    asset = get_object_or_404(Asset, pk=pk)

    # Seul le propriétaire ou le staff peut voir
    if not request.user.is_staff and asset.assigned_to != request.user:
        messages.error(request, _('Accès non autorisé.'))
        return redirect('inventory:my_assets')

    transfers = asset.transfers.select_related('from_user', 'to_user', 'approved_by')
    tickets = asset.tickets.order_by('-created_at')[:5]

    transfer_form = None
    if asset.assigned_to == request.user and not request.user.is_staff:
        transfer_form = AssetTransferForm()

    return render(request, 'inventory/asset_detail.html', {
        'asset': asset,
        'transfers': transfers,
        'tickets': tickets,
        'transfer_form': transfer_form,
        'show_tutorial': _should_show_tutorial(request.user),
    })


# ──────────────────────────────────────────────
# EMPLOYÉ — "MON BUREAU DIGITAL"
# ──────────────────────────────────────────────

@login_required
def my_assets(request):
    """
    Vue employé : liste ses actifs assignés + ses tickets.
    Affiche le tutoriel si pas encore vu.
    """
    my_assets_qs = Asset.objects.filter(
        assigned_to=request.user, status='assigned'
    ).select_related('category')

    my_tickets = Ticket.objects.filter(
        submitted_by=request.user
    ).order_by('-created_at')[:10]

    pending_transfers = AssetTransfer.objects.filter(
        to_user=request.user, status='pending'
    ).select_related('asset', 'from_user')

    context = {
        'my_assets': my_assets_qs,
        'my_tickets': my_tickets,
        'pending_transfers': pending_transfers,
        'open_tickets_count': my_tickets.filter(status__in=['open', 'in_progress']).count() if hasattr(my_tickets, 'filter') else 0,
        'show_tutorial': _should_show_tutorial(request.user),
    }
    return render(request, 'inventory/my_assets.html', context)


@login_required
@require_POST
def request_transfer(request, asset_pk):
    """Demande de transfert P2P d'un actif."""
    asset = get_object_or_404(Asset, pk=asset_pk, assigned_to=request.user)
    form = AssetTransferForm(request.POST)

    if form.is_valid():
        transfer = form.save(commit=False)
        transfer.asset = asset
        transfer.from_user = request.user
        transfer.save()
        messages.success(
            request,
            _(f'Demande de transfert pour {asset.amn_tag} envoyée. En attente d\'approbation.')
        )
    else:
        messages.error(request, _('Erreur dans le formulaire de transfert.'))

    return redirect('inventory:asset_detail', pk=asset_pk)


# ──────────────────────────────────────────────
# HELPDESK — TICKETS SOS
# ──────────────────────────────────────────────

@login_required
def ticket_list(request):
    """Liste des tickets — filtrable par statut et priorité."""
    if request.user.is_staff:
        tickets_qs = Ticket.objects.select_related(
            'submitted_by', 'assigned_to'
        ).order_by('-created_at')
    else:
        tickets_qs = Ticket.objects.filter(
            submitted_by=request.user
        ).order_by('-created_at')

    # Filtres
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    search = request.GET.get('q', '')

    if status_filter:
        tickets_qs = tickets_qs.filter(status=status_filter)
    if priority_filter:
        tickets_qs = tickets_qs.filter(priority=priority_filter)
    if search:
        tickets_qs = tickets_qs.filter(
            Q(subject__icontains=search) |
            Q(ticket_number__icontains=search) |
            Q(description__icontains=search)
        )

    paginator = Paginator(tickets_qs, 15)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page': page,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search': search,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
        'sos_count': Ticket.objects.filter(
            priority='critical', status__in=['open', 'in_progress']
        ).count(),
        'show_tutorial': _should_show_tutorial(request.user),
    }
    return render(request, 'inventory/ticket_list.html', context)


@login_required
def ticket_create(request):
    """Créer un nouveau ticket SOS."""
    form = TicketForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        ticket = form.save(commit=False)
        ticket.submitted_by = request.user
        ticket.save()

        # Notification async si ticket critique
        if ticket.priority == 'critical':
            from .tasks import notify_new_sos_ticket
            notify_new_sos_ticket.apply_async(args=[ticket.pk], countdown=2)

        messages.success(
            request,
            _(f'Ticket #{ticket.ticket_number} ouvert avec succès. Notre équipe vous contactera rapidement.')
        )
        return redirect('inventory:ticket_detail', pk=ticket.pk)

    return render(request, 'inventory/ticket_form.html', {
        'form': form,
        'title': _('Ouvrir un ticket SOS'),
        'show_tutorial': _should_show_tutorial(request.user),
    })


@login_required
def ticket_detail(request, pk):
    """Détail d'un ticket avec fil de commentaires."""
    ticket = get_object_or_404(Ticket, pk=pk)

    # Autorisation : propriétaire ou staff
    if not request.user.is_staff and ticket.submitted_by != request.user:
        messages.error(request, _('Accès non autorisé.'))
        return redirect('inventory:ticket_list')

    # Commentaires
    comments = ticket.comments.select_related('author').all()
    if not request.user.is_staff:
        comments = comments.filter(is_internal=False)

    comment_form = TicketCommentForm()
    status_form = TicketStatusForm(instance=ticket) if request.user.is_staff else None

    if request.method == 'POST':
        action = request.POST.get('action', 'comment')

        if action == 'comment':
            comment_form = TicketCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                # Seul le staff peut poster des notes internes
                if not request.user.is_staff:
                    comment.is_internal = False
                comment.save()
                messages.success(request, _('Commentaire ajouté.'))
                return redirect('inventory:ticket_detail', pk=pk)

        elif action == 'update_status' and request.user.is_staff:
            status_form = TicketStatusForm(request.POST, instance=ticket)
            if status_form.is_valid():
                old_status = ticket.status
                updated = status_form.save(commit=False)
                if updated.status == 'resolved' and not ticket.resolved_at:
                    updated.resolved_at = timezone.now()
                updated.save()

                # Notification employé
                if old_status != updated.status:
                    from .tasks import notify_ticket_update
                    notify_ticket_update.apply_async(
                        args=[ticket.pk, updated.status, request.user.pk],
                        countdown=2,
                    )

                messages.success(request, _('Ticket mis à jour.'))
                return redirect('inventory:ticket_detail', pk=pk)

    return render(request, 'inventory/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'status_form': status_form,
        'show_tutorial': _should_show_tutorial(request.user),
    })


# ──────────────────────────────────────────────
# QR CODE SCAN (AJAX)
# ──────────────────────────────────────────────

@login_required
def qr_lookup(request):
    """
    AJAX — Recherche un actif ou article par son tag/SKU scanné via QR Code.
    Retourne les infos JSON pour affichage instantané.
    """
    code = request.GET.get('code', '').strip()
    if not code:
        return JsonResponse({'found': False, 'error': 'Aucun code fourni'})

    # Chercher dans les actifs
    asset = Asset.objects.filter(amn_tag__iexact=code).first()
    if asset:
        return JsonResponse({
            'found': True,
            'type': 'asset',
            'id': asset.pk,
            'amn_tag': asset.amn_tag,
            'name': asset.name,
            'brand': asset.brand,
            'status': asset.get_status_display(),
            'status_color': asset.status_color,
            'assigned_to': str(asset.assigned_to) if asset.assigned_to else None,
            'redirect_url': f'/inventaire/actifs/{asset.pk}/',
        })

    # Chercher dans le stock
    item = StockItem.objects.filter(sku__iexact=code).first()
    if item:
        badge_color, badge_icon = item.stock_badge
        return JsonResponse({
            'found': True,
            'type': 'stock',
            'id': item.pk,
            'sku': item.sku,
            'name': item.name,
            'quantity': item.quantity,
            'unit': item.get_unit_display(),
            'stock_status': item.stock_status,
            'badge_color': badge_color,
            'badge_icon': badge_icon,
            'redirect_url': f'/inventaire/stock/{item.pk}/transactions/',
        })

    return JsonResponse({'found': False, 'code': code})
