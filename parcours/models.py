from django.db import models
from django.conf import settings


class CareerPath(models.Model):
    """Parcours de carrière recommandé."""
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    tags = models.JSONField(default=list, help_text='Ex: ["Informatique", "Web"]')
    icon = models.CharField(max_length=10, default='💼')
    skills = models.ManyToManyField('competences.Skill', blank=True, related_name='career_paths')

    class Meta:
        verbose_name = 'Parcours de carrière'
        verbose_name_plural = 'Parcours de carrière'

    def __str__(self):
        return self.title

    def get_steps(self):
        return self.steps.all().order_by('order')

    def get_total_cost(self):
        return sum(s.price_fcfa for s in self.steps.all())


class CareerStep(models.Model):
    """Étape dans un parcours de carrière."""
    career = models.ForeignKey(CareerPath, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    is_free = models.BooleanField(default=False, verbose_name='Gratuit')
    price_fcfa = models.IntegerField(default=0, verbose_name='Prix (FCFA)')
    is_premium = models.BooleanField(default=False, verbose_name='Premium')
    duration_hours = models.IntegerField(default=0, verbose_name='Durée (heures)')
    features = models.JSONField(default=list, help_text='Ex: ["Cours vidéo 12h", "8 projets"]')
    icon = models.CharField(max_length=10, default='📘')

    class Meta:
        ordering = ['career', 'order']
        verbose_name = 'Étape de carrière'
        verbose_name_plural = 'Étapes de carrière'

    def __str__(self):
        return f'{self.career.title} — Étape {self.order}: {self.title}'


class StepProject(models.Model):
    """Projet pratique soumis par un étudiant pour valider une étape."""
    STATUS_CHOICES = [
        ('submitted', 'Soumis'),
        ('reviewing', 'En révision'),
        ('approved', 'Approuvé'),
        ('needs_revision', 'À réviser'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='step_projects')
    step = models.ForeignKey(CareerStep, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200, verbose_name='Titre du projet')
    description = models.TextField(verbose_name='Description')
    project_url = models.URLField(blank=True, verbose_name='Lien du projet')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Projet d\'étape'
        verbose_name_plural = 'Projets d\'étape'

    def __str__(self):
        return f'{self.user} — {self.title}'

    @property
    def reviews_count(self):
        return self.peer_reviews.count()

    @property
    def average_rating(self):
        reviews = self.peer_reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)


class PeerReview(models.Model):
    """Évaluation par les pairs d'un projet."""
    project = models.ForeignKey(StepProject, on_delete=models.CASCADE, related_name='peer_reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.IntegerField(verbose_name='Note (1-5)')
    feedback = models.TextField(verbose_name='Commentaire')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'reviewer']
        verbose_name = 'Revue par les pairs'
        verbose_name_plural = 'Revues par les pairs'

    def __str__(self):
        return f'{self.reviewer} → {self.project.title}: {self.rating}/5'


class StepCertificate(models.Model):
    """Certificat généré après complétion d'une étape."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    step = models.ForeignKey(CareerStep, on_delete=models.CASCADE, related_name='certificates')
    certificate_code = models.CharField(max_length=30, unique=True)
    share_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'step']
        verbose_name = 'Certificat'
        verbose_name_plural = 'Certificats'

    def __str__(self):
        return f'{self.user} — {self.step.title} [{self.certificate_code}]'
