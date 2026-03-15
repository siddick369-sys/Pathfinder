from django.db import models
from django.conf import settings


class OrientationQuestion(models.Model):
    """Question du test d'orientation."""
    CATEGORY_CHOICES = [
        ('interest', 'Centre d\'intérêt'),
        ('workstyle', 'Style de travail'),
        ('goal', 'Objectif'),
        ('skill', 'Compétence'),
    ]

    text = models.CharField(max_length=500, verbose_name='Question')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='interest')
    icon = models.CharField(max_length=10, blank=True, default='❓')

    class Meta:
        ordering = ['order']
        verbose_name = 'Question d\'orientation'
        verbose_name_plural = 'Questions d\'orientation'

    def __str__(self):
        return f'Q{self.order}: {self.text[:60]}'


class OrientationChoice(models.Model):
    """Choix de réponse avec poids par carrière."""
    question = models.ForeignKey(OrientationQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300, verbose_name='Texte du choix')
    icon = models.CharField(max_length=10, blank=True, default='')
    weights = models.JSONField(
        default=dict,
        help_text='Poids par carrière: {"fullstack": 3, "chef_projet": 1, "data_analyst": 2}'
    )

    class Meta:
        verbose_name = 'Choix de réponse'
        verbose_name_plural = 'Choix de réponse'

    def __str__(self):
        return f'{self.text[:50]} (Q{self.question.order})'


class OrientationResult(models.Model):
    """Résultat du test d'orientation pour un utilisateur."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orientation_results')
    scores = models.JSONField(
        default=dict,
        help_text='Scores par carrière: {"fullstack": 92, "chef_projet": 78, ...}'
    )
    recommended_career = models.ForeignKey(
        'parcours.CareerPath', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='recommended_for'
    )
    summary = models.TextField(blank=True, verbose_name='Résumé personnalisé')
    career_projection_3y = models.TextField(blank=True, verbose_name='Projection carrière 3 ans')
    priority_skills = models.JSONField(default=list, help_text='Compétences prioritaires')
    selected_choices = models.JSONField(default=dict, help_text='Réponses: {question_id: choice_id}')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Résultat d\'orientation'
        verbose_name_plural = 'Résultats d\'orientation'

    def __str__(self):
        return f'Résultat de {self.user} — {self.created_at.strftime("%d/%m/%Y")}'


class MiniQuiz(models.Model):
    """Mini-quiz hebdomadaire pour affiner le profil."""
    text = models.CharField(max_length=500, verbose_name='Question')
    icon = models.CharField(max_length=10, default='💡')
    week_number = models.IntegerField(default=1, verbose_name='Semaine N°')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['week_number']
        verbose_name = 'Mini-quiz'
        verbose_name_plural = 'Mini-quiz'

    def __str__(self):
        return f'S{self.week_number}: {self.text[:50]}'


class MiniQuizChoice(models.Model):
    """Choix pour un mini-quiz."""
    quiz = models.ForeignKey(MiniQuiz, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    weights = models.JSONField(default=dict, help_text='Poids par carrière')

    def __str__(self):
        return f'{self.text[:50]} (S{self.quiz.week_number})'


class MiniQuizResponse(models.Model):
    """Réponse d'un utilisateur à un mini-quiz."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mini_quiz_responses')
    quiz = models.ForeignKey(MiniQuiz, on_delete=models.CASCADE)
    choice = models.ForeignKey(MiniQuizChoice, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'quiz']
        verbose_name = 'Réponse mini-quiz'
        verbose_name_plural = 'Réponses mini-quiz'
