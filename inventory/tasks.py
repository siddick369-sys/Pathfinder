"""
inventory/tasks.py
Tâches Celery asynchrones — Alertes stock bas & Notifications SOS
"""
from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


@shared_task(bind=True, name='inventory.check_low_stock')
def check_low_stock(self):
    """
    Tâche périodique : vérifie tous les articles en stock.
    Crée une notification pour chaque article sous le seuil d'alerte.
    Planifiée via django-celery-beat (ex : toutes les heures).
    """
    from .models import StockItem
    from notifications.models import Notification
    from django.contrib.auth import get_user_model

    User = get_user_model()

    low_items = StockItem.objects.filter(
        is_active=True,
        quantity__lte=models.F('alert_threshold')
    ).select_related('category')

    # Récupère tous les superusers et staff pour notifier
    admins = User.objects.filter(is_staff=True)
    notified_count = 0

    for item in low_items:
        level = 'critical' if item.quantity == 0 else 'low'
        icon = '🔴' if level == 'critical' else '⚠️'
        label = 'RUPTURE DE STOCK' if level == 'critical' else 'STOCK BAS'

        message = (
            f'{icon} {label} — {item.name} : '
            f'{item.quantity} {item.get_unit_display()} restant(s) '
            f'(seuil : {item.alert_threshold})'
        )

        for admin in admins:
            # Évite les doublons de notification dans la même journée
            today = timezone.now().date()
            already_notified = Notification.objects.filter(
                recipient=admin,
                title__icontains=item.name,
                created_at__date=today,
            ).exists()

            if not already_notified:
                Notification.objects.create(
                    recipient=admin,
                    title=f'Alerte inventaire — {item.name}',
                    message=message,
                    notification_type='warning',
                    link='/inventaire/stock/',
                )
                notified_count += 1

    return {
        'low_items_count': low_items.count(),
        'notifications_sent': notified_count,
        'checked_at': timezone.now().isoformat(),
    }


@shared_task(bind=True, name='inventory.notify_new_sos_ticket')
def notify_new_sos_ticket(self, ticket_id):
    """
    Notifie le staff qu'un nouveau ticket critique (SOS) a été ouvert.
    Appelé dès la création d'un ticket priorité 'critical'.
    """
    from .models import Ticket
    from notifications.models import Notification
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        ticket = Ticket.objects.select_related('submitted_by').get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return {'error': f'Ticket {ticket_id} not found'}

    admins = User.objects.filter(is_staff=True)
    submitted_by_name = str(ticket.submitted_by)

    message = (
        f'🆘 Nouveau ticket SOS de {submitted_by_name} : '
        f'"{ticket.subject}" — Priorité : {ticket.get_priority_display()}'
    )

    for admin in admins:
        Notification.objects.create(
            recipient=admin,
            title=f'🆘 SOS Ticket #{ticket.ticket_number}',
            message=message,
            notification_type='urgent',
            link=f'/inventaire/tickets/{ticket.pk}/',
        )

    return {
        'ticket_number': ticket.ticket_number,
        'notified_staff': admins.count(),
    }


@shared_task(bind=True, name='inventory.notify_ticket_update')
def notify_ticket_update(self, ticket_id, new_status, updated_by_id):
    """
    Notifie l'employé que son ticket a changé de statut.
    """
    from .models import Ticket
    from notifications.models import Notification
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        ticket = Ticket.objects.select_related('submitted_by').get(pk=ticket_id)
        updated_by = User.objects.get(pk=updated_by_id)
    except (Ticket.DoesNotExist, User.DoesNotExist):
        return {'error': 'Object not found'}

    status_labels = {
        'open': 'Ouvert',
        'in_progress': 'Pris en charge',
        'waiting': 'En attente de pièces',
        'resolved': 'Résolu ✅',
        'closed': 'Clôturé',
    }
    label = status_labels.get(new_status, new_status)
    icon = '✅' if new_status == 'resolved' else '🔄'

    Notification.objects.create(
        recipient=ticket.submitted_by,
        title=f'{icon} Ticket #{ticket.ticket_number} — {label}',
        message=(
            f'Votre ticket "{ticket.subject}" a été mis à jour '
            f'par {updated_by} : statut → {label}'
        ),
        notification_type='info',
        link=f'/inventaire/tickets/{ticket.pk}/',
    )

    return {
        'ticket_number': ticket.ticket_number,
        'new_status': new_status,
    }


@shared_task(bind=True, name='inventory.generate_stock_report')
def generate_stock_report(self):
    """
    Génère un rapport mensuel de l'état du stock.
    Peut être planifié le 1er de chaque mois via django-celery-beat.
    """
    from .models import StockItem, StockTransaction
    from django.contrib.auth import get_user_model
    from notifications.models import Notification

    User = get_user_model()

    total_items = StockItem.objects.filter(is_active=True).count()
    low_items = StockItem.objects.filter(
        is_active=True, quantity__lte=models.F('alert_threshold')
    ).count()
    out_of_stock = StockItem.objects.filter(is_active=True, quantity=0).count()

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_transactions = StockTransaction.objects.filter(
        timestamp__gte=month_start
    ).count()

    report_message = (
        f'📊 Rapport mensuel stock ({now:%B %Y}) : '
        f'{total_items} articles actifs, '
        f'{low_items} en alerte, '
        f'{out_of_stock} en rupture, '
        f'{monthly_transactions} mouvements ce mois.'
    )

    for admin in User.objects.filter(is_staff=True):
        Notification.objects.create(
            recipient=admin,
            title=f'📊 Rapport Stock — {now:%B %Y}',
            message=report_message,
            notification_type='info',
            link='/inventaire/stock/',
        )

    return {
        'total_items': total_items,
        'low_items': low_items,
        'out_of_stock': out_of_stock,
        'monthly_transactions': monthly_transactions,
    }


# Import manquant pour les annotations F()
from django.db import models
