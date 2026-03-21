"""
Formulaires — Module Inventaire & Helpdesk.
AMN Employee Hub.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from inventory.models import Asset, StockItem, StockTransaction, Ticket, TicketPriority, TransactionType


class StockUpdateForm(forms.Form):
    """Formulaire de mise à jour rapide du stock (+ ou -)."""

    quantity = forms.IntegerField(
        min_value=1,
        max_value=9999,
        label=_('Quantité'),
        widget=forms.NumberInput(attrs={
            'class': 'w-20 text-center border border-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400',
            'placeholder': '1',
        })
    )

    transaction_type = forms.ChoiceField(
        choices=TransactionType.choices,
        widget=forms.HiddenInput()
    )

    reason = forms.CharField(
        max_length=200,
        required=False,
        label=_('Motif (optionnel)'),
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-slate-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400',
            'placeholder': _('Ex: Livraison fournisseur, Commande bureau…'),
        })
    )


class TicketForm(forms.ModelForm):
    """Formulaire de création d'un ticket helpdesk."""

    class Meta:
        model = Ticket
        fields = ['subject', 'description', 'photo', 'priority', 'asset']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-400 text-slate-800',
                'placeholder': _('Ex: Écran noir au démarrage, Clavier non reconnu…'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-400 text-slate-800 resize-none',
                'rows': 5,
                'placeholder': _('Décrivez le problème en détail : depuis quand, que s\'est-il passé…'),
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-400 text-slate-800',
            }),
            'asset': forms.Select(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-400 text-slate-800',
            }),
            'photo': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'photo-upload',
            }),
        }
        labels = {
            'subject': _('Sujet du problème'),
            'description': _('Description détaillée'),
            'photo': _('Photo de la panne (optionnel)'),
            'priority': _('Niveau d\'urgence'),
            'asset': _('Équipement concerné (optionnel)'),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Filtre les assets assignés à cet employé uniquement
        if user and not user.is_staff:
            self.fields['asset'].queryset = Asset.objects.filter(assigned_to=user)
        self.fields['asset'].required = False
        self.fields['asset'].empty_label = _('— Aucun équipement spécifique —')


class AssetTransferForm(forms.Form):
    """Transfert P2P d'un équipement entre deux employés."""

    new_owner = forms.ModelChoiceField(
        queryset=None,
        label=_('Transférer à'),
        widget=forms.Select(attrs={
            'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
        })
    )

    reason = forms.CharField(
        max_length=200,
        required=False,
        label=_('Motif du transfert'),
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
            'placeholder': _('Ex: Départ en mission, Changement de poste…'),
        })
    )

    def __init__(self, *args, **kwargs):
        from django.contrib.auth import get_user_model
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        User = get_user_model()
        qs = User.objects.filter(is_active=True)
        if current_user:
            qs = qs.exclude(pk=current_user.pk)
        self.fields['new_owner'].queryset = qs


class AssetForm(forms.ModelForm):
    """Formulaire de création/modification d'un équipement (managers uniquement)."""

    class Meta:
        model = Asset
        fields = ['amn_tag', 'category', 'brand', 'serial_number', 'status', 'assigned_to', 'purchase_date', 'notes']
        widgets = {
            'amn_tag': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'placeholder': 'AMN-LT-001',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
            }),
            'brand': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'placeholder': 'Dell Latitude 5520',
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
            }),
            'status': forms.Select(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'type': 'date',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none',
                'rows': 3,
            }),
        }


class StockItemForm(forms.ModelForm):
    """Formulaire de création/modification d'un article de stock."""

    class Meta:
        model = StockItem
        fields = ['name', 'description', 'quantity', 'alert_threshold', 'unit', 'location']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'placeholder': _('Ex: Câble USB-C, Cahier A4…'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none',
                'rows': 2,
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'min': 0,
            }),
            'alert_threshold': forms.NumberInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-orange-400',
                'min': 1,
            }),
            'unit': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'placeholder': 'unité(s), pièce(s), boîte(s)…',
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'placeholder': _('Ex: Armoire A, Étagère 3…'),
            }),
        }
