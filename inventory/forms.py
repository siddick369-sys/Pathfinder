"""
inventory/forms.py
Formulaires pour le Module 3 — Gestion d'Actifs, Stock Global & Helpdesk
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Asset, StockItem, StockTransaction, Ticket, AssetTransfer, TicketComment


class AssetForm(forms.ModelForm):
    """Formulaire de création/édition d'un actif."""

    class Meta:
        model = Asset
        fields = [
            'amn_tag', 'name', 'category', 'brand', 'model',
            'serial_number', 'status', 'assigned_to', 'purchase_date',
            'purchase_price', 'location', 'notes',
        ]
        widgets = {
            'amn_tag': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': 'AMN-PC-0042',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': _('Ex: Laptop Dell Latitude 5520'),
            }),
            'category': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'brand': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': 'Dell, HP, Lenovo…',
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': _('Numéro de modèle'),
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': _('N° de série constructeur'),
            }),
            'status': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control rounded-xl',
                'type': 'date',
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': '0',
                'min': '0',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': _('Siège Douala, Agence Yaoundé…'),
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control rounded-xl',
                'rows': 3,
                'placeholder': _('Remarques optionnelles…'),
            }),
        }


class StockItemForm(forms.ModelForm):
    """Formulaire de création/édition d'un article en stock."""

    class Meta:
        model = StockItem
        fields = [
            'name', 'category', 'quantity', 'alert_threshold',
            'unit', 'location', 'supplier', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': _('Ex: Ramette A4 80g'),
            }),
            'category': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control rounded-xl',
                'min': '0',
            }),
            'alert_threshold': forms.NumberInput(attrs={
                'class': 'form-control rounded-xl',
                'min': '1',
            }),
            'unit': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': _('Étagère 3, Armoire B…'),
            }),
            'supplier': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': _('Nom du fournisseur'),
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control rounded-xl',
                'rows': 2,
                'placeholder': _('Notes optionnelles…'),
            }),
        }


class StockAdjustForm(forms.Form):
    """Formulaire d'ajustement rapide (+/-) du stock."""
    DIRECTION_CHOICES = [
        ('in', _('Entrée (+)')),
        ('out', _('Sortie (-)')),
        ('adjust', _('Ajustement manuel')),
        ('loss', _('Perte / Casse')),
    ]

    direction = forms.ChoiceField(
        choices=DIRECTION_CHOICES,
        label=_('Type de mouvement'),
        widget=forms.Select(attrs={'class': 'form-select rounded-xl'}),
    )
    quantity = forms.IntegerField(
        min_value=1,
        label=_('Quantité'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control rounded-xl',
            'min': '1',
            'value': '1',
        }),
    )
    reason = forms.CharField(
        max_length=255,
        required=False,
        label=_('Motif'),
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-xl',
            'placeholder': _('Optionnel — raison du mouvement'),
        }),
    )
    reference = forms.CharField(
        max_length=100,
        required=False,
        label=_('Référence (N° BL, commande…)'),
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-xl',
            'placeholder': 'BL-2024-XXX',
        }),
    )


class TicketForm(forms.ModelForm):
    """Formulaire de création d'un ticket SOS."""

    class Meta:
        model = Ticket
        fields = [
            'subject', 'category', 'priority', 'description',
            'breakdown_photo', 'related_asset',
        ]
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control rounded-xl',
                'placeholder': _('Résumé court du problème'),
            }),
            'category': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'priority': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control rounded-xl',
                'rows': 5,
                'placeholder': _(
                    'Décrivez le problème en détail : que s\'est-il passé ? '
                    'Depuis quand ? Avez-vous déjà essayé quelque chose ?'
                ),
            }),
            'breakdown_photo': forms.ClearableFileInput(attrs={
                'class': 'form-control rounded-xl',
                'accept': 'image/*',
            }),
            'related_asset': forms.Select(attrs={'class': 'form-select rounded-xl'}),
        }


class TicketStatusForm(forms.ModelForm):
    """Formulaire de mise à jour du statut d'un ticket (staff)."""

    class Meta:
        model = Ticket
        fields = ['status', 'assigned_to', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'form-control rounded-xl',
                'rows': 4,
                'placeholder': _('Notes de résolution, étapes effectuées…'),
            }),
        }


class TicketCommentForm(forms.ModelForm):
    """Formulaire d'ajout d'un commentaire sur un ticket."""

    class Meta:
        model = TicketComment
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control rounded-xl',
                'rows': 3,
                'placeholder': _('Votre message ou mise à jour…'),
            }),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AssetTransferForm(forms.ModelForm):
    """Formulaire de demande de transfert P2P d'un actif."""

    class Meta:
        model = AssetTransfer
        fields = ['to_user', 'reason']
        widgets = {
            'to_user': forms.Select(attrs={'class': 'form-select rounded-xl'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control rounded-xl',
                'rows': 3,
                'placeholder': _('Expliquez pourquoi ce transfert est nécessaire…'),
            }),
        }
