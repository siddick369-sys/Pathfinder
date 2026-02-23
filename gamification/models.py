from django.db import models
from django.conf import settings
from django.utils import timezone


class XPEvent(models.Model):
    """Historique des XP gagnés."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='xp_events')
    action = models.CharField(max_length=100, verbose_name='Action')
    xp_earned = models.IntegerField(verbose_name='XP gagnés')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Événement XP'
        verbose_name_plural = 'Événements XP'

    def __str__(self):
        return f'{self.user}: +{self.xp_earned} XP ({self.action})'


class Badge(models.Model):
    """Badge de progression."""
    CATEGORY_CHOICES = [
        ('progression', 'Progression'),
        ('regularite', 'Régularité'),
        ('excellence', 'Excellence'),
        ('social', 'Social'),
        ('special', 'Spécial'),
    ]
    CONDITION_CHOICES = [
        ('xp_total', 'XP total atteint'),
        ('level_reached', 'Niveau atteint'),
        ('test_complete', 'Test complété'),
        ('steps_completed', 'Étapes complétées'),
        ('streak_days', 'Jours consécutifs'),
        ('skills_unlocked', 'Compétences débloquées'),
        ('payment_made', 'Paiement effectué'),
    ]

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.CharField(max_length=300, verbose_name='Description')
    icon = models.CharField(max_length=10, default='🏅')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='progression')
    condition_type = models.CharField(max_length=30, choices=CONDITION_CHOICES, default='xp_total')
    condition_value = models.IntegerField(default=0, help_text='Seuil numérique')

    class Meta:
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'

    def __str__(self):
        return f'{self.icon} {self.name}'


class UserBadge(models.Model):
    """Badge obtenu par un utilisateur."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='earned_by')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']
        verbose_name = 'Badge utilisateur'
        verbose_name_plural = 'Badges utilisateurs'

    def __str__(self):
        return f'{self.user} — {self.badge.name}'


class Challenge(models.Model):
    """Défi hebdomadaire."""
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    xp_reward = models.IntegerField(default=200, verbose_name='Récompense XP')
    start_date = models.DateField(verbose_name='Début')
    end_date = models.DateField(verbose_name='Fin')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Défi'
        verbose_name_plural = 'Défis'

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class UserChallenge(models.Model):
    """Participation d'un utilisateur à un défi."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'challenge']

    def __str__(self):
        status = '✅' if self.completed else '⏳'
        return f'{status} {self.user} — {self.challenge.title}'


class Booster(models.Model):
    """Article de la boutique éthique."""
    TYPE_CHOICES = [
        ('xp_multiplier', 'Multiplicateur XP'),
        ('ai_analysis', 'Analyse IA Pro'),
        ('pack_competences', 'Pack Compétences'),
        ('theme', 'Thème Profil'),
        ('pack_ambassadeur', 'Pack Ambassadeur'),
    ]

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200, verbose_name='Nom')
    description = models.TextField(verbose_name='Description')
    icon = models.CharField(max_length=10, default='🚀')
    booster_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='xp_multiplier')
    price_fcfa = models.IntegerField(verbose_name='Prix (FCFA)')
    duration_days = models.IntegerField(default=0, help_text='0 = permanent')
    multiplier = models.FloatField(default=1.0, help_text='Multiplicateur XP (ex: 2.0)')

    class Meta:
        verbose_name = 'Booster'
        verbose_name_plural = 'Boosters'

    def __str__(self):
        return f'{self.icon} {self.name} — {self.price_fcfa} FCFA'


class UserBooster(models.Model):
    """Booster activé par un utilisateur."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boosters')
    booster = models.ForeignKey(Booster, on_delete=models.CASCADE, related_name='activations')
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Booster utilisateur'
        verbose_name_plural = 'Boosters utilisateurs'

    def __str__(self):
        return f'{self.user} — {self.booster.name}'

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
