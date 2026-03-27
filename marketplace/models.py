from django.db import models
from django.conf import settings
from django.utils import timezone


class ServiceCategory(models.Model):
    """Catégorie de service sur la marketplace."""
    name = models.CharField(max_length=100, verbose_name='Nom')
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='💼')

    class Meta:
        verbose_name = 'Catégorie de service'
        verbose_name_plural = 'Catégories de services'

    def __str__(self):
        return self.name


class ServiceListing(models.Model):
    """Offre de service publiée par un étudiant."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'En pause'),
        ('closed', 'Fermée'),
    ]
    DELIVERY_CHOICES = [
        ('1', '1 jour'),
        ('3', '3 jours'),
        ('7', '1 semaine'),
        ('14', '2 semaines'),
    ]

    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_listings')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='listings')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    price_fcfa = models.IntegerField(verbose_name='Prix (FCFA)')
    delivery_days = models.CharField(max_length=5, choices=DELIVERY_CHOICES, default='3')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    skills_required = models.ManyToManyField('competences.Skill', blank=True, related_name='marketplace_listings')
    total_orders = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Offre de service'
        verbose_name_plural = 'Offres de services'

    def __str__(self):
        return f'{self.title} par {self.provider}'


class Mission(models.Model):
    """Mission postée par un client (étudiant, entreprise, asso)."""
    STATUS_CHOICES = [
        ('open', 'Ouverte'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_missions')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='missions')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    budget_fcfa = models.IntegerField(verbose_name='Budget (FCFA)')
    deadline = models.DateField(verbose_name='Date limite')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_missions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mission'
        verbose_name_plural = 'Missions'

    def __str__(self):
        return f'{self.title} — {self.budget_fcfa} FCFA'

    @property
    def proposals_count(self):
        return self.proposals.count()


class MissionProposal(models.Model):
    """Candidature d'un prestataire à une mission."""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
    ]

    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='proposals')
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mission_proposals')
    message = models.TextField(verbose_name='Message de candidature')
    proposed_price_fcfa = models.IntegerField(verbose_name='Prix proposé (FCFA)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['mission', 'provider']
        ordering = ['-created_at']
        verbose_name = 'Candidature'
        verbose_name_plural = 'Candidatures'

    def __str__(self):
        return f'{self.provider} → {self.mission.title}'


class ServiceReview(models.Model):
    """Avis sur un service ou une mission terminée."""
    mission = models.OneToOneField(Mission, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    listing = models.ForeignKey(ServiceListing, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_reviews')
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(verbose_name='Note (1-5)')
    comment = models.TextField(blank=True, verbose_name='Commentaire')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avis service'
        verbose_name_plural = 'Avis services'

    def __str__(self):
        return f'{self.reviewer} → {self.provider}: {self.rating}/5'
