from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CareerPath, CareerStep
from orientation.models import OrientationResult
from payments.models import UserProgress


@login_required
def career_view(request):
    """Vue du parcours de carrière avec timeline."""
    result = OrientationResult.objects.filter(user=request.user).first()
    if not result or not result.recommended_career:
        messages.info(request, 'Passez d\'abord le test d\'orientation pour voir votre parcours.')
        return redirect('orientation:test')

    career = result.recommended_career
    progress, _ = UserProgress.objects.get_or_create(user=request.user)
    steps = career.steps.all().order_by('order')

    # Construire la timeline
    timeline = []
    completed_count = 0
    for step in steps:
        is_completed = progress.completed_steps.filter(id=step.id).exists()
        is_unlocked = step.is_free or progress.unlocked_steps.filter(id=step.id).exists()
        if is_completed:
            completed_count += 1
        timeline.append({
            'step': step,
            'is_completed': is_completed,
            'is_unlocked': is_unlocked,
            'status': 'completed' if is_completed else ('active' if is_unlocked else 'locked'),
        })

    total_steps = steps.count()
    progress_pct = (completed_count / total_steps * 100) if total_steps > 0 else 0

    context = {
        'career': career,
        'timeline': timeline,
        'completed_count': completed_count,
        'total_steps': total_steps,
        'progress_pct': round(progress_pct),
    }
    return render(request, 'parcours/carriere.html', context)


@login_required
def complete_step(request, step_id):
    """Marque une étape comme complétée."""
    step = get_object_or_404(CareerStep, id=step_id)
    progress, _ = UserProgress.objects.get_or_create(user=request.user)

    if step.is_free or progress.unlocked_steps.filter(id=step.id).exists():
        progress.completed_steps.add(step)
        progress.recalculate()
        request.user.add_xp(75, action=f'etape_completee:{step.title}')
        messages.success(request, f'Étape "{step.title}" complétée ! +75 XP')
    else:
        messages.warning(request, 'Cette étape doit d\'abord être débloquée.')

    return redirect('parcours:career')
