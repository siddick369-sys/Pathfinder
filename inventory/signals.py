"""
Signaux Django pour le module Inventaire.
Déclenche les tâches Celery après création/modification.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from inventory.models import StockItem, StockTransaction, Ticket


@receiver(post_save, sender=StockTransaction)
def check_stock_level_after_transaction(sender, instance, created, **kwargs):
    """Vérifie le niveau de stock après chaque transaction et déclenche une alerte si nécessaire."""
    if created and instance.item.is_low_stock:
        from inventory.tasks import notify_low_stock
        notify_low_stock.delay(instance.item.pk)


@receiver(post_save, sender=Ticket)
def notify_new_ticket(sender, instance, created, **kwargs):
    """Notifie les responsables à la création d'un nouveau ticket SOS."""
    if created and instance.is_sos:
        from inventory.tasks import notify_new_sos_ticket
        notify_new_sos_ticket.delay(instance.pk)
