from django.db import models
from django.conf import settings


class PaymentSimulation(models.Model):
    """Simulation de paiement (aucune transaction réelle)."""
    METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money (MTN)'),
        ('orange_money', 'Orange Money'),
        ('carte', 'Carte bancaire'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    step = models.ForeignKey('parcours.CareerStep', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    skill = models.ForeignKey('competences.Skill', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    booster = models.ForeignKey('gamification.Booster', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount_fcfa = models.IntegerField(verbose_name='Montant (FCFA)')
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='mobile_money')
    phone_number = models.CharField(max_length=20, blank=True)
    holder_name = models.CharField(max_length=100, blank=True, verbose_name='Nom du titulaire')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Simulation de paiement'
        verbose_name_plural = 'Simulations de paiement'

    def __str__(self):
        label = self.step or self.skill or self.booster or 'Autre'
        return f'{self.user} — {self.amount_fcfa} FCFA — {label}'


class UserProgress(models.Model):
    """Suivi de progression globale de l'utilisateur."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    completed_steps = models.ManyToManyField('parcours.CareerStep', blank=True, related_name='completed_by')
    unlocked_steps = models.ManyToManyField('parcours.CareerStep', blank=True, related_name='unlocked_by')
    global_percent = models.FloatField(default=0.0, verbose_name='Progression %')

    class Meta:
        verbose_name = 'Progression utilisateur'
        verbose_name_plural = 'Progressions utilisateurs'

    def __str__(self):
        return f'{self.user} — {self.global_percent:.0f}%'

    def recalculate(self):
        """Recalcule la progression globale à partir des étapes."""
        from parcours.models import CareerStep
        from orientation.models import OrientationResult
        result = OrientationResult.objects.filter(user=self.user).first()
        if result and result.recommended_career:
            total = result.recommended_career.steps.count()
            done = self.completed_steps.filter(career=result.recommended_career).count()
            self.global_percent = (done / total * 100) if total > 0 else 0
            self.save(update_fields=['global_percent'])
            self.user.global_progress = self.global_percent
            self.user.save(update_fields=['global_progress'])
