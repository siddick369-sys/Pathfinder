"""
Migration initiale — Module Inventaire & Helpdesk.
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amn_tag', models.CharField(help_text="Identifiant unique de l'équipement (ex: AMN-LT-001)", max_length=30, unique=True, verbose_name='Tag AMN')),
                ('category', models.CharField(choices=[('LAPTOP', 'Laptop / Ordinateur portable'), ('DESKTOP', 'Desktop / Ordinateur fixe'), ('PHONE', 'Téléphone mobile'), ('TABLET', 'Tablette'), ('MONITOR', 'Écran / Moniteur'), ('KEYBOARD', 'Clavier'), ('MOUSE', 'Souris'), ('HEADSET', 'Casque audio'), ('BADGE', "Badge / Carte d'accès"), ('OTHER', 'Autre équipement')], default='OTHER', max_length=20, verbose_name='Catégorie')),
                ('brand', models.CharField(max_length=60, verbose_name='Marque / Modèle')),
                ('serial_number', models.CharField(blank=True, max_length=100, verbose_name='Numéro de série')),
                ('status', models.CharField(choices=[('AVAILABLE', 'Disponible'), ('ASSIGNED', 'Assigné'), ('IN_REPAIR', 'En réparation'), ('LOST', 'Perdu / Volé'), ('RETIRED', 'Mis au rebut')], default='AVAILABLE', max_length=20, verbose_name='Statut')),
                ('assigned_at', models.DateTimeField(blank=True, null=True, verbose_name="Date d'assignation")),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('purchase_date', models.DateField(blank=True, null=True, verbose_name="Date d'achat")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets', to=settings.AUTH_USER_MODEL, verbose_name='Assigné à')),
            ],
            options={
                'verbose_name': 'Équipement',
                'verbose_name_plural': 'Équipements',
                'ordering': ['amn_tag'],
            },
        ),
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name="Nom de l'article")),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Quantité en stock')),
                ('alert_threshold', models.PositiveIntegerField(default=5, help_text='Notification envoyée quand la quantité passe sous ce seuil', verbose_name="Seuil d'alerte")),
                ('unit', models.CharField(default='unité(s)', max_length=30, verbose_name='Unité')),
                ('location', models.CharField(blank=True, max_length=80, verbose_name='Emplacement / Étagère')),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='inventory/qrcodes/', verbose_name='QR Code')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Article de stock',
                'verbose_name_plural': 'Articles de stock',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StockTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('IN', 'Entrée de stock'), ('OUT', 'Sortie de stock')], max_length=3, verbose_name='Type de mouvement')),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantité')),
                ('quantity_before', models.PositiveIntegerField(verbose_name='Stock avant')),
                ('quantity_after', models.PositiveIntegerField(verbose_name='Stock après')),
                ('reason', models.CharField(blank=True, max_length=200, verbose_name='Motif')),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Horodatage')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='inventory.stockitem', verbose_name='Article')),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_transactions', to=settings.AUTH_USER_MODEL, verbose_name='Effectué par')),
            ],
            options={
                'verbose_name': 'Mouvement de stock',
                'verbose_name_plural': 'Mouvements de stock',
                'ordering': ['-timestamp'],
                'default_permissions': ('add', 'view'),
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=160, verbose_name='Sujet')),
                ('description', models.TextField(verbose_name='Description du problème')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='inventory/tickets/%Y/%m/', verbose_name='Photo de la panne')),
                ('priority', models.CharField(choices=[('LOW', 'Basse'), ('MEDIUM', 'Moyenne'), ('HIGH', 'Haute'), ('SOS', 'SOS — Critique')], default='MEDIUM', max_length=10, verbose_name='Priorité')),
                ('status', models.CharField(choices=[('OPEN', 'Ouvert'), ('IN_PROGRESS', 'En cours'), ('RESOLVED', 'Résolu'), ('CLOSED', 'Fermé')], default='OPEN', max_length=15, verbose_name='Statut')),
                ('resolution_notes', models.TextField(blank=True, verbose_name='Notes de résolution')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('asset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets', to='inventory.asset', verbose_name='Équipement concerné')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL, verbose_name='Assigné à')),
                ('submitted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets', to=settings.AUTH_USER_MODEL, verbose_name='Soumis par')),
            ],
            options={
                'verbose_name': 'Ticket Helpdesk',
                'verbose_name_plural': 'Tickets Helpdesk',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['status'], name='inventory_a_status_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['assigned_to'], name='inventory_a_assigned_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['category'], name='inventory_a_category_idx'),
        ),
        migrations.AddIndex(
            model_name='stockitem',
            index=models.Index(fields=['quantity', 'alert_threshold'], name='inventory_s_qty_alert_idx'),
        ),
        migrations.AddIndex(
            model_name='stocktransaction',
            index=models.Index(fields=['timestamp'], name='inventory_st_ts_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['status', 'priority'], name='inventory_t_status_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['submitted_by'], name='inventory_t_submitted_idx'),
        ),
    ]
