"""
inventory/models.py
Module 3 AMN Employee Hub — Gestion d'Actifs, Stock Global & Helpdesk
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ──────────────────────────────────────────────
# ASSETS INDIVIDUELS
# ──────────────────────────────────────────────

class AssetCategory(models.Model):
    """Catégorie de matériel (PC, Téléphone, Mobilier…)."""
    name = models.CharField(_('Nom'), max_length=100)
    icon = models.CharField(max_length=10, default='📦')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _('Catégorie d\'actif')
        verbose_name_plural = _('Catégories d\'actif')
        ordering = ['name']

    def __str__(self):
        return f'{self.icon} {self.name}'


class Asset(models.Model):
    """Actif individuel assigné à un employé."""
    STATUS_CHOICES = [
        ('available', _('Disponible')),
        ('assigned', _('Assigné')),
        ('maintenance', _('En maintenance')),
        ('retired', _('Mis hors service')),
        ('lost', _('Perdu / Volé')),
    ]

    amn_tag = models.CharField(
        _('Tag AMN'), max_length=50, unique=True,
        help_text=_('Identifiant unique AMN (ex: AMN-PC-0042)')
    )
    name = models.CharField(_('Désignation'), max_length=200)
    category = models.ForeignKey(
        AssetCategory, on_delete=models.SET_NULL, null=True,
        related_name='assets', verbose_name=_('Catégorie')
    )
    brand = models.CharField(_('Marque'), max_length=100, blank=True)
    model = models.CharField(_('Modèle'), max_length=100, blank=True)
    serial_number = models.CharField(_('N° Série'), max_length=100, blank=True)
    status = models.CharField(
        _('Statut'), max_length=20, choices=STATUS_CHOICES, default='available'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_assets',
        verbose_name=_('Assigné à')
    )
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Date d\'attribution'))
    purchase_date = models.DateField(null=True, blank=True, verbose_name=_('Date d\'achat'))
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name=_('Valeur d\'achat (FCFA)')
    )
    location = models.CharField(_('Localisation'), max_length=150, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    qr_code = models.ImageField(
        upload_to='inventory/qr_codes/', blank=True, verbose_name=_('QR Code')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Actif')
        verbose_name_plural = _('Actifs')
        ordering = ['amn_tag']

    def __str__(self):
        return f'[{self.amn_tag}] {self.name}'

    @property
    def status_color(self):
        colors = {
            'available': 'success',
            'assigned': 'primary',
            'maintenance': 'warning',
            'retired': 'secondary',
            'lost': 'danger',
        }
        return colors.get(self.status, 'secondary')

    @property
    def status_icon(self):
        icons = {
            'available': '✅',
            'assigned': '👤',
            'maintenance': '🔧',
            'retired': '🗄️',
            'lost': '❌',
        }
        return icons.get(self.status, '📦')


class AssetTransfer(models.Model):
    """Transfert P2P d'un actif entre deux employés."""
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('approved', _('Approuvé')),
        ('rejected', _('Refusé')),
        ('completed', _('Complété')),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE,
                              related_name='transfers', verbose_name=_('Actif'))
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='transfers_sent', verbose_name=_('Cédant')
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='transfers_received', verbose_name=_('Bénéficiaire')
    )
    reason = models.TextField(_('Motif du transfert'))
    status = models.CharField(
        _('Statut'), max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_transfers',
        verbose_name=_('Approuvé par')
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Transfert d\'actif')
        verbose_name_plural = _('Transferts d\'actifs')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.asset.amn_tag}: {self.from_user} → {self.to_user}'


# ──────────────────────────────────────────────
# STOCK GLOBAL (CONSOMMABLES)
# ──────────────────────────────────────────────

class StockItem(models.Model):
    """Article en stock (consommables, fournitures)."""
    UNIT_CHOICES = [
        ('unit', _('Unité')),
        ('box', _('Boîte')),
        ('ream', _('Ramette')),
        ('liter', _('Litre')),
        ('kg', _('Kg')),
        ('pack', _('Pack')),
    ]

    name = models.CharField(_('Désignation'), max_length=200)
    sku = models.CharField(
        _('Référence SKU'), max_length=50, unique=True, blank=True,
        help_text=_('Laissez vide pour génération automatique')
    )
    category = models.ForeignKey(
        AssetCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_items', verbose_name=_('Catégorie')
    )
    quantity = models.PositiveIntegerField(_('Quantité actuelle'), default=0)
    alert_threshold = models.PositiveIntegerField(
        _('Seuil d\'alerte'), default=5,
        help_text=_('Déclenche une alerte si la quantité descend en dessous')
    )
    unit = models.CharField(_('Unité'), max_length=10, choices=UNIT_CHOICES, default='unit')
    location = models.CharField(_('Emplacement'), max_length=150, blank=True)
    supplier = models.CharField(_('Fournisseur'), max_length=200, blank=True)
    last_restock_date = models.DateField(null=True, blank=True, verbose_name=_('Dernier réappro'))
    notes = models.TextField(_('Notes'), blank=True)
    is_active = models.BooleanField(_('Actif'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Article en stock')
        verbose_name_plural = _('Articles en stock')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.quantity} {self.get_unit_display()})'

    def save(self, *args, **kwargs):
        if not self.sku:
            import random
            import string
            self.sku = 'STK-' + ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
        super().save(*args, **kwargs)

    @property
    def stock_status(self):
        """Retourne le niveau d'alerte : ok / low / critical."""
        if self.quantity == 0:
            return 'critical'
        if self.quantity <= self.alert_threshold:
            return 'low'
        return 'ok'

    @property
    def stock_badge(self):
        badges = {
            'ok': ('success', '✅'),
            'low': ('warning', '⚠️'),
            'critical': ('danger', '🔴'),
        }
        return badges.get(self.stock_status, ('secondary', '📦'))

    @property
    def is_low_stock(self):
        return self.quantity <= self.alert_threshold


class StockTransaction(models.Model):
    """Journal immuable de chaque mouvement de stock (Audit Trail)."""
    TYPE_CHOICES = [
        ('in', _('Entrée')),
        ('out', _('Sortie')),
        ('adjust', _('Ajustement')),
        ('loss', _('Perte / Casse')),
    ]

    item = models.ForeignKey(
        StockItem, on_delete=models.CASCADE,
        related_name='transactions', verbose_name=_('Article')
    )
    transaction_type = models.CharField(
        _('Type'), max_length=10, choices=TYPE_CHOICES
    )
    quantity = models.IntegerField(
        _('Quantité'), help_text=_('Positif pour entrée, négatif pour sortie')
    )
    quantity_before = models.PositiveIntegerField(_('Stock avant'), default=0)
    quantity_after = models.PositiveIntegerField(_('Stock après'), default=0)
    reason = models.CharField(_('Motif'), max_length=255, blank=True)
    reference = models.CharField(
        _('Référence'), max_length=100, blank=True,
        help_text=_('N° BL, N° commande, etc.')
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='stock_transactions',
        verbose_name=_('Effectué par')
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Date/Heure'))

    class Meta:
        verbose_name = _('Mouvement de stock')
        verbose_name_plural = _('Mouvements de stock')
        ordering = ['-timestamp']
        # Immutabilité : pas de mise à jour possible
        default_permissions = ('add', 'view')

    def __str__(self):
        sign = '+' if self.quantity > 0 else ''
        return f'{self.item.name} | {sign}{self.quantity} | {self.timestamp:%d/%m/%Y %H:%M}'

    @property
    def type_icon(self):
        icons = {'in': '📥', 'out': '📤', 'adjust': '🔄', 'loss': '💔'}
        return icons.get(self.transaction_type, '📋')

    @property
    def type_color(self):
        colors = {'in': 'success', 'out': 'primary', 'adjust': 'warning', 'loss': 'danger'}
        return colors.get(self.transaction_type, 'secondary')


# ──────────────────────────────────────────────
# HELPDESK / TICKETS SOS
# ──────────────────────────────────────────────

class Ticket(models.Model):
    """Ticket de support SOS pour pannes ou demandes matérielles."""
    PRIORITY_CHOICES = [
        ('low', _('Faible')),
        ('medium', _('Moyenne')),
        ('high', _('Haute')),
        ('critical', _('Critique / SOS')),
    ]
    STATUS_CHOICES = [
        ('open', _('Ouvert')),
        ('in_progress', _('En cours')),
        ('waiting', _('En attente de pièces')),
        ('resolved', _('Résolu')),
        ('closed', _('Fermé')),
    ]
    CATEGORY_CHOICES = [
        ('hardware', _('Matériel informatique')),
        ('software', _('Logiciel / Application')),
        ('network', _('Réseau / Internet')),
        ('phone', _('Téléphonie')),
        ('furniture', _('Mobilier / Locaux')),
        ('other', _('Autre')),
    ]

    ticket_number = models.CharField(
        _('N° Ticket'), max_length=20, unique=True, editable=False
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='submitted_tickets', verbose_name=_('Soumis par')
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tickets',
        verbose_name=_('Assigné à')
    )
    related_asset = models.ForeignKey(
        Asset, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tickets', verbose_name=_('Actif concerné')
    )
    subject = models.CharField(_('Sujet'), max_length=200)
    description = models.TextField(_('Description du problème'))
    breakdown_photo = models.ImageField(
        upload_to='inventory/tickets/', blank=True,
        verbose_name=_('Photo de la panne')
    )
    category = models.CharField(
        _('Catégorie'), max_length=20, choices=CATEGORY_CHOICES, default='hardware'
    )
    priority = models.CharField(
        _('Priorité'), max_length=10, choices=PRIORITY_CHOICES, default='medium'
    )
    status = models.CharField(
        _('Statut'), max_length=20, choices=STATUS_CHOICES, default='open'
    )
    resolution_notes = models.TextField(_('Notes de résolution'), blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Ticket Support')
        verbose_name_plural = _('Tickets Support')
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.ticket_number}] {self.subject} — {self.get_priority_display()}'

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import random
            year = timezone.now().year
            self.ticket_number = f'TKT-{year}-{random.randint(10000, 99999)}'
        super().save(*args, **kwargs)

    @property
    def priority_color(self):
        colors = {
            'low': 'secondary',
            'medium': 'primary',
            'high': 'warning',
            'critical': 'danger',
        }
        return colors.get(self.priority, 'secondary')

    @property
    def priority_icon(self):
        icons = {
            'low': '🟢',
            'medium': '🔵',
            'high': '🟠',
            'critical': '🔴',
        }
        return icons.get(self.priority, '⚪')

    @property
    def status_color(self):
        colors = {
            'open': 'danger',
            'in_progress': 'warning',
            'waiting': 'secondary',
            'resolved': 'success',
            'closed': 'dark',
        }
        return colors.get(self.status, 'secondary')

    @property
    def is_sos(self):
        return self.priority == 'critical'


class TicketComment(models.Model):
    """Commentaire interne sur un ticket."""
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='comments', verbose_name=_('Ticket')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name=_('Auteur')
    )
    content = models.TextField(_('Commentaire'))
    is_internal = models.BooleanField(
        _('Note interne'), default=False,
        help_text=_('Si coché, visible uniquement par le staff')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Commentaire ticket')
        verbose_name_plural = _('Commentaires tickets')
        ordering = ['created_at']

    def __str__(self):
        return f'{self.ticket.ticket_number} — {self.author} ({self.created_at:%d/%m %H:%M})'
