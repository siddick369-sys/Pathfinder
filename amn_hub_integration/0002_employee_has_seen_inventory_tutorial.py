"""
Migration : ajout du champ has_seen_inventory_tutorial sur Employee.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='has_seen_inventory_tutorial',
            field=models.BooleanField(
                default=False,
                help_text="True si l'employé a déjà vu le tutoriel du module Inventaire",
                verbose_name='Tutoriel inventaire vu',
            ),
        ),
    ]
