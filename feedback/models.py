from django.db import models
from django.conf import settings


class Feedback(models.Model):
    """Retour utilisateur."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.CharField(max_length=200, verbose_name='Sujet')
    message = models.TextField(verbose_name='Message')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Retour'
        verbose_name_plural = 'Retours'

    def __str__(self):
        return f'{self.user} — {self.subject}'
