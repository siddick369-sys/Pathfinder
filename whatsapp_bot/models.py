from django.db import models
from django.conf import settings


class WhatsAppSubscriber(models.Model):
    """Abonné WhatsApp lié ou non à un compte PathFinder."""
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='Numéro WhatsApp')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_profile')
    name = models.CharField(max_length=100, blank=True, verbose_name='Nom')
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False, verbose_name='Premium (micro-lessons)')
    daily_lesson_enabled = models.BooleanField(default=True, verbose_name='Leçons quotidiennes')
    reminder_enabled = models.BooleanField(default=True, verbose_name='Rappels activés')
    current_quiz_step = models.IntegerField(default=0, help_text='Étape actuelle du quiz d\'orientation')
    quiz_answers = models.JSONField(default=dict, help_text='Réponses au quiz en cours')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Abonné WhatsApp'
        verbose_name_plural = 'Abonnés WhatsApp'

    def __str__(self):
        return f'{self.phone_number} — {self.name or "Inconnu"}'


class MicroLesson(models.Model):
    """Micro-leçon quotidienne envoyée par WhatsApp."""
    LEVEL_CHOICES = [
        ('free', 'Gratuit'),
        ('premium', 'Premium'),
    ]

    title = models.CharField(max_length=200, verbose_name='Titre')
    content = models.TextField(verbose_name='Contenu (max 500 caractères recommandés)')
    skill = models.ForeignKey('competences.Skill', on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='free')
    order = models.IntegerField(default=0, verbose_name='Ordre d\'envoi')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Micro-leçon'
        verbose_name_plural = 'Micro-leçons'

    def __str__(self):
        return f'{self.title} ({self.get_level_display()})'


class WhatsAppMessage(models.Model):
    """Historique des messages WhatsApp envoyés/reçus."""
    DIRECTION_CHOICES = [
        ('incoming', 'Reçu'),
        ('outgoing', 'Envoyé'),
    ]

    subscriber = models.ForeignKey(WhatsAppSubscriber, on_delete=models.CASCADE, related_name='messages')
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    content = models.TextField()
    message_type = models.CharField(max_length=30, default='text', help_text='text, quiz, lesson, reminder, result')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Message WhatsApp'
        verbose_name_plural = 'Messages WhatsApp'

    def __str__(self):
        return f'{self.subscriber.phone_number} [{self.direction}] {self.content[:50]}'


class ShareableResult(models.Model):
    """Résultat d'orientation partageable (image générée pour WhatsApp)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shareable_results')
    career_name = models.CharField(max_length=200)
    match_percentage = models.IntegerField()
    share_code = models.CharField(max_length=20, unique=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Résultat partageable'
        verbose_name_plural = 'Résultats partageables'

    def __str__(self):
        return f'{self.user} — {self.career_name} ({self.match_percentage}%)'
