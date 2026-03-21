from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import time


class WorkSchedule(models.Model):
    """Planning de travail hebdomadaire AMN."""
    SHIFT_CHOICES = [
        ('matin', 'Matin (07h-15h)'),
        ('journee', 'Journée (08h-17h)'),
        ('apres_midi', 'Après-midi (13h-21h)'),
        ('nuit', 'Nuit (21h-06h)'),
        ('flexible', 'Flexible'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='work_schedules', verbose_name='Employé')
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='journee')
    start_time = models.TimeField(default=time(8, 0), verbose_name='Heure de début')
    end_time = models.TimeField(default=time(17, 0), verbose_name='Heure de fin')
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    effective_from = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Planning de travail'
        verbose_name_plural = 'Plannings de travail'
        ordering = ['-effective_from']

    def __str__(self):
        return f'{self.user} — {self.get_shift_display()} (depuis {self.effective_from})'


class AttendanceRecord(models.Model):
    """Enregistrement de présence journalier."""
    STATUS_CHOICES = [
        ('present', '✅ Présent'),
        ('absent', '❌ Absent'),
        ('late', '⚠️ En retard'),
        ('half_day', '🌗 Demi-journée'),
        ('remote', '🏠 Télétravail'),
        ('on_leave', '🏖️ En congé'),
        ('sick', '🤒 Maladie'),
        ('holiday', '🎉 Jour férié'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='attendance_records', verbose_name='Employé')
    date = models.DateField(verbose_name='Date')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    check_in = models.TimeField(null=True, blank=True, verbose_name='Heure d\'arrivée')
    check_out = models.TimeField(null=True, blank=True, verbose_name='Heure de départ')
    working_hours = models.FloatField(default=0.0, verbose_name='Heures travaillées')
    overtime_hours = models.FloatField(default=0.0, verbose_name='Heures supplémentaires')
    notes = models.TextField(blank=True, verbose_name='Remarques')
    location = models.CharField(max_length=100, blank=True, verbose_name='Lieu',
                                help_text='Ex: Siège Douala, Agence Yaoundé, Télétravail')
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='validated_attendances',
                                     verbose_name='Validé par')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        verbose_name = 'Présence'
        verbose_name_plural = 'Présences'
        ordering = ['-date']

    def __str__(self):
        return f'{self.user} — {self.date} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            h_in = self.check_in.hour + self.check_in.minute / 60
            h_out = self.check_out.hour + self.check_out.minute / 60
            total = h_out - h_in
            self.working_hours = max(0, round(total - 1.0, 2))  # -1h pause déjeuner
            self.overtime_hours = max(0, round(self.working_hours - 8.0, 2))
        super().save(*args, **kwargs)

    @property
    def is_late(self):
        return self.status == 'late'

    @property
    def duration_display(self):
        if self.working_hours:
            h = int(self.working_hours)
            m = int((self.working_hours - h) * 60)
            return f'{h}h{m:02d}'
        return '—'


class LeaveRequest(models.Model):
    """Demande de congé ou d'absence."""
    TYPE_CHOICES = [
        ('annual', '🏖️ Congé annuel'),
        ('sick', '🤒 Congé maladie'),
        ('maternity', '👶 Congé maternité/paternité'),
        ('unpaid', '💼 Congé sans solde'),
        ('training', '🎓 Formation externe'),
        ('emergency', '🆘 Urgence familiale'),
        ('other', '📋 Autre'),
    ]
    STATUS_CHOICES = [
        ('pending', '⏳ En attente'),
        ('approved', '✅ Approuvé'),
        ('rejected', '❌ Refusé'),
        ('cancelled', '🚫 Annulé'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='leave_requests', verbose_name='Employé')
    leave_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='annual')
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    reason = models.TextField(verbose_name='Motif')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='reviewed_leaves',
                                    verbose_name='Traité par')
    review_comment = models.TextField(blank=True, verbose_name='Commentaire RH')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Demande de congé'
        verbose_name_plural = 'Demandes de congé'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} — {self.get_leave_type_display()} ({self.start_date} → {self.end_date})'

    @property
    def duration_days(self):
        delta = self.end_date - self.start_date
        return delta.days + 1

    @property
    def status_color(self):
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
        }
        return colors.get(self.status, 'secondary')


class AttendanceSummary(models.Model):
    """Récapitulatif mensuel de présence par employé."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='attendance_summaries')
    year = models.PositiveIntegerField(verbose_name='Année')
    month = models.PositiveIntegerField(verbose_name='Mois')
    present_days = models.PositiveIntegerField(default=0)
    absent_days = models.PositiveIntegerField(default=0)
    late_days = models.PositiveIntegerField(default=0)
    leave_days = models.PositiveIntegerField(default=0)
    total_hours = models.FloatField(default=0.0)
    overtime_hours = models.FloatField(default=0.0)
    attendance_rate = models.FloatField(default=0.0, verbose_name='Taux de présence (%)')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'year', 'month']
        verbose_name = 'Récap mensuel présence'
        verbose_name_plural = 'Récaps mensuels présence'
        ordering = ['-year', '-month']

    def __str__(self):
        return f'{self.user} — {self.month:02d}/{self.year} ({self.attendance_rate:.1f}%)'
