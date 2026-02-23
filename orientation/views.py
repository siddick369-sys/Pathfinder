from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import OrientationQuestion, OrientationResult
from .engine import process_orientation
from parcours.models import CareerPath


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
    """Vue des résultats d'orientation."""
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

    context = {
        'result': result,
        'top_careers': top_careers,
    }
    return render(request, 'orientation/resultats.html', context)
