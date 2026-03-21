"""
Modèles du Module 3 — Inventaire, Stock Global & Helpdesk.
AMN Employee Hub.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ─────────────────────────────────────────────────────────────────────────────
# CHOICES
# ─────────────────────────────────────────────────────────────────────────────

class AssetCategory(models.TextChoices):
    LAPTOP      = 'LAPTOP',     _('Laptop / Ordinateur portable')
    DESKTOP     = 'DESKTOP',    _('Desktop / Ordinateur fixe')
    PHONE       = 'PHONE',      _('Téléphone mobile')
    TABLET      = 'TABLET',     _('Tablette')
    MONITOR     = 'MONITOR',    _('Écran / Moniteur')
    KEYBOARD    = 'KEYBOARD',   _('Clavier')
    MOUSE       = 'MOUSE',      _('Souris')
    HEADSET     = 'HEADSET',    _('Casque audio')
    BADGE       = 'BADGE',      _('Badge / Carte d\'accès')
    OTHER       = 'OTHER',      _('Autre équipement')


class AssetStatus(models.TextChoices):
    AVAILABLE   = 'AVAILABLE',  _('Disponible')
    ASSIGNED    = 'ASSIGNED',   _('Assigné')
    IN_REPAIR   = 'IN_REPAIR',  _('En réparation')
    LOST        = 'LOST',       _('Perdu / Volé')
    RETIRED     = 'RETIRED',    _('Mis au rebut')


class TransactionType(models.TextChoices):
    IN   = 'IN',   _('Entrée de stock')
    OUT  = 'OUT',  _('Sortie de stock')


class TicketPriority(models.TextChoices):
    LOW      = 'LOW',    _('Basse')
    MEDIUM   = 'MEDIUM', _('Moyenne')
    HIGH     = 'HIGH',   _('Haute')
    CRITICAL = 'SOS',    _('SOS — Critique')


class TicketStatus(models.TextChoices):
    OPEN        = 'OPEN',       _('Ouvert')
    IN_PROGRESS = 'IN_PROGRESS', _('En cours')
    RESOLVED    = 'RESOLVED',   _('Résolu')
    CLOSED      = 'CLOSED',     _('Fermé')


# ─────────────────────────────────────────────────────────────────────────────
# ASSET — Matériel individuel assigné à un employé
# ─────────────────────────────────────────────────────────────────────────────

class Asset(models.Model):
    """Équipement individuel tracé par tag AMN."""

    amn_tag = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_('Tag AMN'),
        help_text=_('Identifiant unique de l\'équipement (ex: AMN-LT-001)')
    )

    category = models.CharField(
        max_length=20,
        choices=AssetCategory.choices,
        default=AssetCategory.OTHER,
        verbose_name=_('Catégorie')
    )

    brand = models.CharField(
        max_length=60,
        verbose_name=_('Marque / Modèle')
    )

    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Numéro de série')
    )

    status = models.CharField(
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.AVAILABLE,
        verbose_name=_('Statut')
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets',
        verbose_name=_('Assigné à')
    )

    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Date d\'assignation')
    )

    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )

    purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date d\'achat')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Équipement')
        verbose_name_plural = _('Équipements')
        ordering = ['amn_tag']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f'{self.amn_tag} — {self.brand} ({self.get_category_display()})'

    def assign_to(self, employee):
        """Assigne cet équipement à un employé."""
        self.assigned_to = employee
        self.status = AssetStatus.ASSIGNED
        self.assigned_at = timezone.now()
        self.save(update_fields=['assigned_to', 'status', 'assigned_at'])

    def release(self):
        """Libère l'équipement."""
        self.assigned_to = None
        self.status = AssetStatus.AVAILABLE
        self.assigned_at = None
        self.save(update_fields=['assigned_to', 'status', 'assigned_at'])


# ─────────────────────────────────────────────────────────────────────────────
# STOCK GLOBAL — Consommables et fournitures
# ─────────────────────────────────────────────────────────────────────────────

class StockItem(models.Model):
    """Article de stock global (consommables, fournitures)."""

    name = models.CharField(
        max_length=120,
        verbose_name=_('Nom de l\'article')
    )

    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )

    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Quantité en stock')
    )

    alert_threshold = models.PositiveIntegerField(
        default=5,
        verbose_name=_('Seuil d\'alerte'),
        help_text=_('Notification envoyée quand la quantité passe sous ce seuil')
    )

    unit = models.CharField(
        max_length=30,
        default='unité(s)',
        verbose_name=_('Unité')
    )

    location = models.CharField(
        max_length=80,
        blank=True,
        verbose_name=_('Emplacement / Étagère')
    )

    qr_code = models.ImageField(
        upload_to='inventory/qrcodes/',
        blank=True,
        null=True,
        verbose_name=_('QR Code')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Article de stock')
        verbose_name_plural = _('Articles de stock')
        ordering = ['name']
        indexes = [
            models.Index(fields=['quantity', 'alert_threshold']),
        ]

    def __str__(self):
        return f'{self.name} ({self.quantity} {self.unit})'

    @property
    def is_low_stock(self):
        return self.quantity <= self.alert_threshold

    @property
    def is_critical_stock(self):
        return self.quantity <= max(1, self.alert_threshold // 2)

    @property
    def stock_level(self):
        """Retourne 'ok', 'low' ou 'critical' pour le template."""
        if self.is_critical_stock:
            return 'critical'
        if self.is_low_stock:
            return 'low'
        return 'ok'


class StockTransaction(models.Model):
    """
    Journal immuable de chaque mouvement de stock.
    Audit trail : ne jamais modifier, seulement créer.
    """

    item = models.ForeignKey(
        StockItem,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name=_('Article')
    )

    transaction_type = models.CharField(
        max_length=3,
        choices=TransactionType.choices,
        verbose_name=_('Type de mouvement')
    )

    quantity = models.PositiveIntegerField(
        verbose_name=_('Quantité')
    )

    quantity_before = models.PositiveIntegerField(
        verbose_name=_('Stock avant')
    )

    quantity_after = models.PositiveIntegerField(
        verbose_name=_('Stock après')
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_transactions',
        verbose_name=_('Effectué par')
    )

    reason = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Motif')
    )

    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name=_('Horodatage')
    )

    class Meta:
        verbose_name = _('Mouvement de stock')
        verbose_name_plural = _('Mouvements de stock')
        ordering = ['-timestamp']
        # Audit trail : lecture seule après création
        default_permissions = ('add', 'view')

    def __str__(self):
        direction = '↑' if self.transaction_type == TransactionType.IN else '↓'
        return f'{direction} {self.item.name} × {self.quantity} — {self.timestamp:%Y-%m-%d %H:%M}'

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError(_('Les mouvements de stock sont immuables (audit trail).'))
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# TICKET HELPDESK
# ─────────────────────────────────────────────────────────────────────────────

class Ticket(models.Model):
    """Ticket de support technique soumis par un employé."""

    subject = models.CharField(
        max_length=160,
        verbose_name=_('Sujet')
    )

    description = models.TextField(
        verbose_name=_('Description du problème')
    )

    photo = models.ImageField(
        upload_to='inventory/tickets/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Photo de la panne')
    )

    priority = models.CharField(
        max_length=10,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
        verbose_name=_('Priorité')
    )

    status = models.CharField(
        max_length=15,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN,
        verbose_name=_('Statut')
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tickets',
        verbose_name=_('Soumis par')
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name=_('Assigné à')
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name=_('Équipement concerné')
    )

    resolution_notes = models.TextField(
        blank=True,
        verbose_name=_('Notes de résolution')
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Ticket Helpdesk')
        verbose_name_plural = _('Tickets Helpdesk')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['submitted_by']),
        ]

    def __str__(self):
        return f'[{self.get_priority_display()}] {self.subject}'

    @property
    def is_sos(self):
        return self.priority == TicketPriority.CRITICAL

    def resolve(self, agent, notes=''):
        self.status = TicketStatus.RESOLVED
        self.assigned_to = agent
        self.resolution_notes = notes
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'assigned_to', 'resolution_notes', 'resolved_at'])
