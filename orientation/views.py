from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import OrientationQuestion, OrientationResult, MiniQuiz, MiniQuizChoice, MiniQuizResponse
from .engine import process_orientation
from parcours.models import CareerPath
from accounts.models import CustomUser


@login_required
def test_view(request):
    """Vue du test d'orientation avec quiz interactif."""
    questions = OrientationQuestion.objects.prefetch_related('choices').order_by('order')

    if request.method == 'POST':
        selected_choices = {}
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                selected_choices[str(question.id)] = int(choice_id)

        if len(selected_choices) < questions.count():
            messages.warning(request, 'Veuillez répondre à toutes les questions.')
            return render(request, 'orientation/test.html', {
                'questions': questions,
                'selected': selected_choices,
            })

        result = process_orientation(request.user, selected_choices)
        return redirect('orientation:results')

    return render(request, 'orientation/test.html', {'questions': questions})


@login_required
def results_view(request):
    """Vue des résultats d'orientation avec comparaison sociale."""
    result = OrientationResult.objects.filter(user=request.user).first()
    if not result:
        messages.info(request, 'Vous n\'avez pas encore passé le test d\'orientation.')
        return redirect('orientation:test')

    # Préparer les top carrières pour le template
    top_careers = []
    for slug, pct in list(result.scores.items())[:3]:
        try:
            career = CareerPath.objects.get(slug=slug)
            top_careers.append({'career': career, 'percentage': pct, 'slug': slug})
        except CareerPath.DoesNotExist:
            top_careers.append({'career': None, 'percentage': pct, 'slug': slug})

    # Comparaison sociale : combien d'étudiants ont le même métier recommandé
    social_stats = {}
    if result.recommended_career:
        total_results = OrientationResult.objects.count()
        same_career = OrientationResult.objects.filter(recommended_career=result.recommended_career).count()
        if total_results > 0:
            social_stats = {
                'same_career_pct': round(same_career / total_results * 100),
                'same_career_count': same_career,
                'total_users': total_results,
            }

    # Mini-quiz disponible
    answered_ids = MiniQuizResponse.objects.filter(user=request.user).values_list('quiz_id', flat=True)
    pending_quiz = MiniQuiz.objects.filter(is_active=True).exclude(id__in=answered_ids).first()

    context = {
        'result': result,
        'top_careers': top_careers,
        'social_stats': social_stats,
        'pending_quiz': pending_quiz,
    }
    return render(request, 'orientation/resultats.html', context)


@login_required
def mini_quiz_view(request):
    """Mini-quiz hebdomadaire (3 questions rapides)."""
    answered_ids = MiniQuizResponse.objects.filter(user=request.user).values_list('quiz_id', flat=True)
    quizzes = MiniQuiz.objects.filter(is_active=True).exclude(id__in=answered_ids).prefetch_related('choices')[:3]

    if not quizzes:
        messages.info(request, 'Aucun mini-quiz disponible cette semaine. Revenez bientôt !')
        return redirect('orientation:results')

    if request.method == 'POST':
        for quiz in quizzes:
            choice_id = request.POST.get(f'mini_quiz_{quiz.id}')
            if choice_id:
                try:
                    choice = MiniQuizChoice.objects.get(id=choice_id)
                    MiniQuizResponse.objects.get_or_create(
                        user=request.user,
                        quiz=quiz,
                        defaults={'choice': choice}
                    )
                except MiniQuizChoice.DoesNotExist:
                    pass

        request.user.add_xp(20, action='mini_quiz_complete')
        messages.success(request, 'Mini-quiz terminé ! +20 XP. Votre profil a été affiné.')
        return redirect('orientation:results')

    context = {'quizzes': quizzes}
    return render(request, 'orientation/mini_quiz.html', context)
