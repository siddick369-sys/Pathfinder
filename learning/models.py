from django.db import models
from django.conf import settings
from django.utils import timezone


class Department(models.Model):
    """Département AMN."""
    name = models.CharField(max_length=100, verbose_name='Nom')
    code = models.CharField(max_length=10, unique=True, verbose_name='Code')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🏢')
    head_name = models.CharField(max_length=150, blank=True, verbose_name='Responsable')

    class Meta:
        verbose_name = 'Département'
        verbose_name_plural = 'Départements'
        ordering = ['name']

    def __str__(self):
        return f'{self.icon} {self.name}'


class TrainingModule(models.Model):
    """Module de formation AMN (ex: Module 2 - Réseau Mobile)."""
    LEVEL_CHOICES = [
        ('debutant', 'Débutant'),
        ('intermediaire', 'Intermédiaire'),
        ('avance', 'Avancé'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]

    number = models.PositiveIntegerField(verbose_name='Numéro du module')
    title = models.CharField(max_length=200, verbose_name='Titre')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Description')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='modules', verbose_name='Département')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='debutant')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    duration_hours = models.PositiveIntegerField(default=0, verbose_name='Durée estimée (heures)')
    objectives = models.JSONField(default=list, help_text='Liste des objectifs pédagogiques')
    prerequisites = models.TextField(blank=True, verbose_name='Prérequis')
    cover_image_url = models.URLField(blank=True, verbose_name='Image de couverture (URL)')
    is_mandatory = models.BooleanField(default=False, verbose_name='Formation obligatoire')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Module de formation'
        verbose_name_plural = 'Modules de formation'
        ordering = ['order', 'number']

    def __str__(self):
        return f'Module {self.number} — {self.title}'

    def get_courses_count(self):
        return self.courses.count()

    def get_total_lessons(self):
        return Lesson.objects.filter(course__module=self).count()

    def get_enrolled_count(self):
        return self.enrollments.count()

    @property
    def level_badge(self):
        badges = {
            'debutant': ('🟢', 'success'),
            'intermediaire': ('🟡', 'warning'),
            'avance': ('🔴', 'danger'),
        }
        return badges.get(self.level, ('⚪', 'secondary'))


class Course(models.Model):
    """Cours au sein d'un module de formation."""
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE,
                               related_name='courses', verbose_name='Module')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name='Durée (min)')
    instructor_name = models.CharField(max_length=150, blank=True, verbose_name='Formateur')
    instructor_title = models.CharField(max_length=200, blank=True, verbose_name='Titre du formateur')
    cover_image_url = models.URLField(blank=True, verbose_name='Image (URL)')
    xp_reward = models.PositiveIntegerField(default=50, verbose_name='XP à la complétion')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
        ordering = ['module', 'order']

    def __str__(self):
        return f'{self.module.title} › {self.title}'

    def get_lessons_count(self):
        return self.lessons.count()


class Lesson(models.Model):
    """Leçon individuelle dans un cours."""
    TYPE_CHOICES = [
        ('video', '🎬 Vidéo'),
        ('article', '📄 Article'),
        ('quiz', '❓ Quiz'),
        ('exercise', '✏️ Exercice'),
        ('pdf', '📋 PDF'),
        ('live', '📡 Présentiel/Live'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='lessons', verbose_name='Cours')
    title = models.CharField(max_length=200, verbose_name='Titre')
    lesson_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='article')
    content = models.TextField(verbose_name='Contenu')
    video_url = models.URLField(blank=True, verbose_name='URL vidéo')
    pdf_url = models.URLField(blank=True, verbose_name='URL PDF')
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=15, verbose_name='Durée (min)')
    xp_reward = models.PositiveIntegerField(default=20)
    is_free_preview = models.BooleanField(default=False, verbose_name='Aperçu gratuit')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Leçon'
        verbose_name_plural = 'Leçons'
        ordering = ['course', 'order']

    def __str__(self):
        return f'{self.course.title} › Leçon {self.order}: {self.title}'

    @property
    def type_icon(self):
        icons = {
            'video': '🎬', 'article': '📄', 'quiz': '❓',
            'exercise': '✏️', 'pdf': '📋', 'live': '📡',
        }
        return icons.get(self.lesson_type, '📁')


class Quiz(models.Model):
    """Quiz associé à une leçon."""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE,
                                  related_name='quiz', verbose_name='Leçon')
    passing_score = models.PositiveIntegerField(default=70, verbose_name='Score minimum (%)')
    time_limit_minutes = models.PositiveIntegerField(default=15, verbose_name='Limite de temps (min)')
    max_attempts = models.PositiveIntegerField(default=3, verbose_name='Tentatives max')

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'

    def __str__(self):
        return f'Quiz — {self.lesson.title}'


class QuizQuestion(models.Model):
    """Question d'un quiz."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name='Question')
    explanation = models.TextField(blank=True, verbose_name='Explication de la réponse')
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['quiz', 'order']
        verbose_name = 'Question de quiz'
        verbose_name_plural = 'Questions de quiz'

    def __str__(self):
        return f'Q{self.order}: {self.text[:80]}'


class QuizChoice(models.Model):
    """Choix de réponse pour une question de quiz."""
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500, verbose_name='Réponse')
    is_correct = models.BooleanField(default=False, verbose_name='Correcte')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['question', 'order']
        verbose_name = 'Choix de réponse'
        verbose_name_plural = 'Choix de réponse'

    def __str__(self):
        return f'{"✅" if self.is_correct else "❌"} {self.text[:60]}'


class Enrollment(models.Model):
    """Inscription d'un employé à un module de formation."""
    STATUS_CHOICES = [
        ('enrolled', 'Inscrit'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('dropped', 'Abandonné'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='enrollments', verbose_name='Employé')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE,
                               related_name='enrollments', verbose_name='Module')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.FloatField(default=0.0, verbose_name='Progression (%)')
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name='Dernière activité')

    class Meta:
        unique_together = ['user', 'module']
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.user} → {self.module.title} ({self.get_status_display()})'

    def recalculate_progress(self):
        total = Lesson.objects.filter(course__module=self.module).count()
        if total == 0:
            return
        completed = LessonProgress.objects.filter(
            user=self.user, lesson__course__module=self.module, completed=True
        ).count()
        self.progress_percent = round((completed / total) * 100, 1)
        if self.progress_percent >= 100:
            self.status = 'completed'
            if not self.completed_at:
                self.completed_at = timezone.now()
        elif self.progress_percent > 0:
            self.status = 'in_progress'
        self.last_activity = timezone.now()
        self.save(update_fields=['progress_percent', 'status', 'completed_at', 'last_activity'])


class LessonProgress(models.Model):
    """Suivi de complétion d'une leçon par un employé."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0, verbose_name='Temps passé (min)')
    notes = models.TextField(blank=True, verbose_name='Notes personnelles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name = 'Progression leçon'
        verbose_name_plural = 'Progressions leçons'

    def __str__(self):
        return f'{"✅" if self.completed else "⏳"} {self.user} — {self.lesson.title}'

    def mark_complete(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=['completed', 'completed_at'])
        enrollment, _ = Enrollment.objects.get_or_create(
            user=self.user, module=self.lesson.course.module
        )
        enrollment.recalculate_progress()


class QuizAttempt(models.Model):
    """Tentative de quiz par un employé."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField(default=0.0, verbose_name='Score (%)')
    passed = models.BooleanField(default=False)
    answers = models.JSONField(default=dict, help_text='Réponses choisies par question')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Tentative de quiz'
        verbose_name_plural = 'Tentatives de quiz'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} — {self.quiz.lesson.title}: {self.score:.0f}%'


class Certificate(models.Model):
    """Certificat de complétion de module."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='certificates')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE,
                               related_name='certificates')
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE,
                                      related_name='certificate', null=True)
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0.0, verbose_name='Score final (%)')
    is_valid = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Certificat'
        verbose_name_plural = 'Certificats'
        ordering = ['-issued_at']

    def __str__(self):
        return f'Cert #{self.certificate_number} — {self.user} ({self.module.title})'

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import random
            import string
            self.certificate_number = 'AMN-' + ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
        super().save(*args, **kwargs)
