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
