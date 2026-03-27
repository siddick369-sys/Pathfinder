from django.db import models
from django.conf import settings
from django.utils import timezone


class MentorProfile(models.Model):
    """Profil de mentor — accessible dès Level 4+."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_profile')
    bio = models.TextField(verbose_name='Présentation', help_text='Décrivez votre parcours et expertise')
    specialties = models.JSONField(default=list, help_text='Ex: ["Python", "Marketing digital"]')
    university = models.CharField(max_length=200, blank=True, verbose_name='Université')
    is_available = models.BooleanField(default=True, verbose_name='Disponible')
    hourly_rate_fcfa = models.IntegerField(default=500, verbose_name='Tarif / 30 min (FCFA)')
    total_sessions = models.IntegerField(default=0, verbose_name='Sessions effectuées')
    average_rating = models.FloatField(default=0.0, verbose_name='Note moyenne')
    total_reviews = models.IntegerField(default=0, verbose_name='Nombre d\'avis')
    is_verified = models.BooleanField(default=False, verbose_name='Vérifié')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Profil mentor'
        verbose_name_plural = 'Profils mentors'

    def __str__(self):
        return f'Mentor: {self.user}'

    @property
    def display_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def can_be_mentor(self):
        return self.user.level >= 4


class MentorSession(models.Model):
    """Session de mentorat réservée."""
    TYPE_CHOICES = [
        ('visio', 'Visioconférence'),
        ('chat', 'Chat en ligne'),
        ('presentiel', 'Présentiel'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]

    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='sessions')
    mentee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentee_sessions')
    session_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='chat')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date = models.DateField(verbose_name='Date')
    time_slot = models.CharField(max_length=20, verbose_name='Créneau horaire')
    duration_minutes = models.IntegerField(default=30, verbose_name='Durée (min)')
    price_fcfa = models.IntegerField(default=0, verbose_name='Prix (FCFA)')
    is_free_intro = models.BooleanField(default=False, verbose_name='Session découverte gratuite')
    topic = models.CharField(max_length=300, blank=True, verbose_name='Sujet')
    notes = models.TextField(blank=True, verbose_name='Notes de session')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Session de mentorat'
        verbose_name_plural = 'Sessions de mentorat'

    def __str__(self):
        return f'{self.mentee} → {self.mentor} ({self.date})'


class MentorReview(models.Model):
    """Avis sur un mentor après une session."""
    session = models.OneToOneField(MentorSession, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_reviews')
    rating = models.IntegerField(verbose_name='Note (1-5)')
    comment = models.TextField(blank=True, verbose_name='Commentaire')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avis mentor'
        verbose_name_plural = 'Avis mentors'

    def __str__(self):
        return f'{self.reviewer} → {self.session.mentor} : {self.rating}/5'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        profile = self.session.mentor
        reviews = MentorReview.objects.filter(session__mentor=profile)
        profile.average_rating = round(sum(r.rating for r in reviews) / max(reviews.count(), 1), 1)
        profile.total_reviews = reviews.count()
        profile.save(update_fields=['average_rating', 'total_reviews'])


class StudyGroup(models.Model):
    """Groupe d'étude créé par un mentor."""
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='study_groups')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    max_members = models.IntegerField(default=10, verbose_name='Places max')
    price_per_member_fcfa = models.IntegerField(default=500, verbose_name='Prix par membre (FCFA)')
    skill = models.ForeignKey('competences.Skill', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Groupe d\'étude'
        verbose_name_plural = 'Groupes d\'étude'

    def __str__(self):
        return f'{self.title} par {self.mentor}'

    @property
    def members_count(self):
        return self.members.count()

    @property
    def is_full(self):
        return self.members_count >= self.max_members


class StudyGroupMember(models.Model):
    """Membre d'un groupe d'étude."""
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['group', 'user']
        verbose_name = 'Membre du groupe'
        verbose_name_plural = 'Membres du groupe'

    def __str__(self):
        return f'{self.user} dans {self.group.title}'
