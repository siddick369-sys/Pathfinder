"""
Tâches Celery — Module Inventaire & Helpdesk.
AMN Employee Hub.
"""

import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def notify_low_stock(self, stock_item_id: int):
    """
    Envoie une notification email aux responsables stock
    quand un article passe sous le seuil d'alerte.
    """
    try:
        from inventory.models import StockItem
        from django.contrib.auth import get_user_model

        item = StockItem.objects.get(pk=stock_item_id)
        User = get_user_model()

        # Notifie les managers (staff)
        managers = User.objects.filter(is_staff=True, is_active=True).values_list('email', flat=True)
        managers = [e for e in managers if e]

        if not managers:
            logger.warning('Aucun manager trouvé pour la notification stock bas.')
            return

        level = 'CRITIQUE' if item.is_critical_stock else 'BAS'
        subject = f'[AMN Hub] ⚠️ Stock {level} — {item.name}'
        message = (
            f'Alerte Inventaire AMN Employee Hub\n\n'
            f'Article : {item.name}\n'
            f'Quantité actuelle : {item.quantity} {item.unit}\n'
            f'Seuil d\'alerte : {item.alert_threshold} {item.unit}\n'
            f'Niveau : {level}\n\n'
            f'Veuillez réapprovisionner cet article.\n'
            f'Emplacement : {item.location or "Non précisé"}\n'
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(managers),
            fail_silently=False,
        )
        logger.info(f'Notification stock bas envoyée pour {item.name} à {len(managers)} managers.')

    except Exception as exc:
        logger.error(f'Erreur notify_low_stock: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def notify_new_sos_ticket(self, ticket_id: int):
    """
    Notifie immédiatement les managers IT lors d'un ticket SOS critique.
    """
    try:
        from inventory.models import Ticket
        from django.contrib.auth import get_user_model

        ticket = Ticket.objects.select_related('submitted_by').get(pk=ticket_id)
        User = get_user_model()

        managers = User.objects.filter(is_staff=True, is_active=True).values_list('email', flat=True)
        managers = [e for e in managers if e]

        if not managers:
            logger.warning('Aucun manager IT trouvé pour la notification SOS.')
            return

        submitter = ticket.submitted_by
        submitter_name = submitter.get_full_name() if submitter else 'Inconnu'

        subject = f'[AMN Hub] 🚨 SOS TICKET #{ticket.pk} — Action requise'
        message = (
            f'TICKET SOS — Intervention urgente requise\n\n'
            f'Ticket #{ticket.pk}\n'
            f'Soumis par : {submitter_name}\n'
            f'Sujet : {ticket.subject}\n'
            f'Description :\n{ticket.description}\n\n'
            f'Accédez au tableau de bord Helpdesk pour traiter ce ticket en priorité.\n'
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(managers),
            fail_silently=False,
        )
        logger.info(f'Notification SOS ticket #{ticket.pk} envoyée à {len(managers)} managers.')

    except Exception as exc:
        logger.error(f'Erreur notify_new_sos_ticket: {exc}')
        raise self.retry(exc=exc, countdown=30)


@shared_task
def generate_stock_qr_codes():
    """
    Tâche périodique : génère/régénère les QR codes pour les articles sans code.
    """
    try:
        import qrcode
        import io
        from django.core.files.base import ContentFile
        from inventory.models import StockItem

        items = StockItem.objects.filter(qr_code='')
        count = 0

        for item in items:
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(f'AMN-STOCK-{item.pk}')
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            filename = f'stock_{item.pk}.png'
            item.qr_code.save(filename, ContentFile(buffer.read()), save=True)
            count += 1

        logger.info(f'{count} QR codes générés.')
        return count

    except Exception as e:
        logger.error(f'Erreur generate_stock_qr_codes: {e}')
        raise
