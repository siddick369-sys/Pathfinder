from django.db import models
from django.conf import settings


class Skill(models.Model):
    """Compétence stratégique."""
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200, verbose_name='Nom')
    description = models.TextField(verbose_name='Description')
    icon = models.CharField(max_length=10, default='💡')
    max_level = models.IntegerField(default=5, verbose_name='Niveau max')
    is_premium = models.BooleanField(default=False, verbose_name='Premium')
    price_fcfa = models.IntegerField(default=0, verbose_name='Prix (FCFA)')

    class Meta:
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'

    def __str__(self):
        return self.name


class SkillResource(models.Model):
    """Ressource pédagogique liée à une compétence."""
    RESOURCE_TYPES = [
        ('video', '🎬 Vidéo'),
        ('pdf', '📄 Document PDF'),
        ('tutoriel', '📝 Tutoriel'),
        ('lien', '🔗 Lien externe'),
        ('exercice', '✏️ Exercice pratique'),
        ('mini_formation', '🎓 Mini-formation'),
    ]

    LEVELS = [
        ('debutant', '🟢 Débutant'),
        ('intermediaire', '🟡 Intermédiaire'),
        ('avance', '🔴 Avancé'),
    ]

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(blank=True, verbose_name='Description')
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES, default='video')
    level = models.CharField(max_length=20, choices=LEVELS, default='debutant', verbose_name='Niveau')
    url = models.URLField(blank=True, verbose_name='Lien externe')
    file = models.FileField(upload_to='resources/pdf/', blank=True, verbose_name='Fichier PDF')
    content = models.TextField(blank=True, verbose_name='Contenu du tutoriel',
                               help_text='Contenu texte pour les tutoriels intégrés')
    duration_minutes = models.IntegerField(default=0, verbose_name='Durée (min)')
    order = models.IntegerField(default=0, verbose_name='Ordre')
    xp_reward = models.IntegerField(default=25, verbose_name='XP gagné')
    is_free_preview = models.BooleanField(default=False, verbose_name='Aperçu gratuit',
                                          help_text='Accessible même sans paiement')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ressource'
        verbose_name_plural = 'Ressources'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.title} ({self.get_resource_type_display()})'

    @property
    def type_icon(self):
        icons = {'video': '🎬', 'pdf': '📄', 'tutoriel': '📝',
                 'lien': '🔗', 'exercice': '✏️', 'mini_formation': '🎓'}
        return icons.get(self.resource_type, '📁')

    @property
    def level_color(self):
        colors = {'debutant': '#22c55e', 'intermediaire': '#f59e0b', 'avance': '#ef4444'}
        return colors.get(self.level, '#6b7280')


class UserSkillProgress(models.Model):
    """Progression d'un utilisateur sur une compétence."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_progress')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_progress')
    current_level = models.IntegerField(default=0, verbose_name='Niveau actuel')
    progress_percent = models.FloatField(default=0.0, verbose_name='Progression %')
    unlocked = models.BooleanField(default=False, verbose_name='Débloqué')

    class Meta:
        unique_together = ['user', 'skill']
        verbose_name = 'Progression compétence'
        verbose_name_plural = 'Progressions compétences'

    def __str__(self):
        return f'{self.user} — {self.skill.name}: {self.progress_percent:.0f}%'

    @property
    def level_label(self):
        labels = {0: 'Non commencé', 1: 'Débutant', 2: 'Débutant avancé',
                  3: 'Intermédiaire', 4: 'Avancé', 5: 'Expert'}
        return labels.get(self.current_level, 'Expert')

    def recalculate_progress(self):
        """Recalcule la progression basée sur les ressources complétées."""
        total = self.skill.resources.count()
        if total == 0:
            return
        completed = UserResourceProgress.objects.filter(
            user=self.user, resource__skill=self.skill, completed=True
        ).count()
        self.progress_percent = round((completed / total) * 100, 1)
        # Calculer le niveau (1 par tranche de 20%)
        self.current_level = min(self.skill.max_level, int(self.progress_percent / 20))
        self.save()


class UserResourceProgress(models.Model):
    """Suivi de completion d'une ressource par un utilisateur."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resource_progress')
    resource = models.ForeignKey(SkillResource, on_delete=models.CASCADE, related_name='user_completions')
    completed = models.BooleanField(default=False, verbose_name='Terminé')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Date de completion')
    notes = models.TextField(blank=True, verbose_name='Notes personnelles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'resource']
        verbose_name = 'Progression ressource'
        verbose_name_plural = 'Progressions ressources'

    def __str__(self):
        status = '✅' if self.completed else '⏳'
        return f'{status} {self.user} — {self.resource.title}'
