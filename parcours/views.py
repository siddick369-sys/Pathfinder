import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CareerPath, CareerStep, StepProject, PeerReview, StepCertificate
from orientation.models import OrientationResult
from payments.models import UserProgress
from notifications.models import Notification


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
        has_certificate = StepCertificate.objects.filter(user=request.user, step=step).exists()
        if is_completed:
            completed_count += 1
        timeline.append({
            'step': step,
            'is_completed': is_completed,
            'is_unlocked': is_unlocked,
            'has_certificate': has_certificate,
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
    """Marque une étape comme complétée et génère un certificat."""
    step = get_object_or_404(CareerStep, id=step_id)
    progress, _ = UserProgress.objects.get_or_create(user=request.user)

    if step.is_free or progress.unlocked_steps.filter(id=step.id).exists():
        progress.completed_steps.add(step)
        progress.recalculate()
        request.user.add_xp(75, action=f'etape_completee:{step.title}')

        # Générer un certificat
        cert, created = StepCertificate.objects.get_or_create(
            user=request.user,
            step=step,
            defaults={'certificate_code': uuid.uuid4().hex[:12].upper()}
        )
        if created:
            Notification.objects.create(
                user=request.user,
                title=f'Certificat obtenu ! 🎓',
                message=f'Vous avez obtenu le certificat "{step.title}". Partagez-le !',
                notification_type='achievement',
                link=f'/parcours/certificat/{cert.certificate_code}/'
            )

        messages.success(request, f'Étape "{step.title}" complétée ! +75 XP 🎓 Certificat généré !')
    else:
        messages.warning(request, 'Cette étape doit d\'abord être débloquée.')

    return redirect('parcours:career')


@login_required
def submit_project(request, step_id):
    """Soumettre un projet pratique pour une étape."""
    step = get_object_or_404(CareerStep, id=step_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        project_url = request.POST.get('project_url', '').strip()

        if not title or not description:
            messages.error(request, 'Titre et description sont obligatoires.')
            return render(request, 'parcours/submit_project.html', {'step': step})

        project = StepProject.objects.create(
            user=request.user,
            step=step,
            title=title,
            description=description,
            project_url=project_url,
        )
        request.user.add_xp(30, action='projet_soumis')
        messages.success(request, 'Projet soumis ! +30 XP. En attente de revue par les pairs.')
        return redirect('parcours:projects_list', step_id=step_id)

    context = {'step': step}
    return render(request, 'parcours/submit_project.html', context)


@login_required
def projects_list(request, step_id):
    """Liste des projets soumis pour une étape (peer review)."""
    step = get_object_or_404(CareerStep, id=step_id)
    projects = StepProject.objects.filter(step=step).select_related('user').order_by('-created_at')

    context = {
        'step': step,
        'projects': projects,
    }
    return render(request, 'parcours/projects_list.html', context)


@login_required
def review_project(request, project_id):
    """Évaluer le projet d'un pair."""
    project = get_object_or_404(StepProject, pk=project_id)

    if project.user == request.user:
        messages.error(request, 'Vous ne pouvez pas évaluer votre propre projet.')
        return redirect('parcours:projects_list', step_id=project.step.id)

    if PeerReview.objects.filter(project=project, reviewer=request.user).exists():
        messages.info(request, 'Vous avez déjà évalué ce projet.')
        return redirect('parcours:projects_list', step_id=project.step.id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 3))
        rating = max(1, min(5, rating))
        feedback = request.POST.get('feedback', '').strip()

        PeerReview.objects.create(
            project=project,
            reviewer=request.user,
            rating=rating,
            feedback=feedback,
        )
        request.user.add_xp(15, action='peer_review_donnee')

        # Notifier l'auteur du projet
        Notification.objects.create(
            user=project.user,
            title='Nouvelle revue ! 📝',
            message=f'{request.user.first_name} a évalué votre projet "{project.title}" ({rating}/5).',
            notification_type='info',
        )

        # Auto-approuver si >= 3 revues avec moyenne >= 3.5
        if project.reviews_count >= 3 and project.average_rating >= 3.5:
            project.status = 'approved'
            project.save(update_fields=['status'])
            project.user.add_xp(50, action='projet_approuve_pairs')

        messages.success(request, 'Revue envoyée ! +15 XP')
        return redirect('parcours:projects_list', step_id=project.step.id)

    context = {'project': project}
    return render(request, 'parcours/review_project.html', context)


def certificate_view(request, code):
    """Vue publique d'un certificat (partageable)."""
    cert = get_object_or_404(StepCertificate, certificate_code=code)
    cert.share_count += 1
    cert.save(update_fields=['share_count'])
    context = {'cert': cert}
    return render(request, 'parcours/certificate.html', context)
