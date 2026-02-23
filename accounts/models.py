from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Utilisateur PathFinder étendu."""
    FILIERE_CHOICES = [
        ('informatique', 'Informatique'),
        ('gestion', 'Gestion'),
        ('marketing', 'Marketing'),
        ('communication', 'Communication'),
        ('droit', 'Droit'),
        ('sciences', 'Sciences'),
        ('lettres', 'Lettres'),
        ('autre', 'Autre'),
    ]
    NIVEAU_CHOICES = [
        ('licence1', 'Licence 1'),
        ('licence2', 'Licence 2'),
        ('licence3', 'Licence 3'),
        ('master1', 'Master 1'),
        ('master2', 'Master 2'),
        ('doctorat', 'Doctorat'),
    ]

    filiere = models.CharField(max_length=100, choices=FILIERE_CHOICES, blank=True)
    niveau = models.CharField(max_length=50, choices=NIVEAU_CHOICES, blank=True)
    avatar_initials = models.CharField(max_length=3, blank=True)
    global_progress = models.FloatField(default=0.0, help_text='Progression globale 0-100%')
    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def save(self, *args, **kwargs):
        if not self.avatar_initials and self.first_name and self.last_name:
            self.avatar_initials = (self.first_name[0] + self.last_name[0]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}' if self.first_name else self.username

    def recalculate_level(self):
        """Calcul niveau : XP requis = 100 × N^1.5"""
        import math
        n = 1
        while 100 * (n ** 1.5) <= self.total_xp:
            n += 1
        self.level = max(1, n - 1)

    def add_xp(self, amount, action=''):
        """Ajouter de l'XP et recalculer le niveau."""
        from gamification.models import XPEvent
        self.total_xp += amount
        self.recalculate_level()
        self.save(update_fields=['total_xp', 'level'])
        XPEvent.objects.create(user=self, action=action, xp_earned=amount)

    @property
    def level_name(self):
        names = {1: 'Explorateur', 2: 'Apprenti', 3: 'Pratiquant',
                 4: 'Confirmé', 5: 'Expert', 6: 'Mentor', 7: 'Architecte'}
        return names.get(min(self.level, 7), 'Architecte')

    @property
    def level_icon(self):
        icons = {1: '🌱', 2: '📘', 3: '⚡', 4: '🎯', 5: '🏆', 6: '💎', 7: '👑'}
        return icons.get(min(self.level, 7), '👑')
