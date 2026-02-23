from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Skill, SkillResource, UserSkillProgress, UserResourceProgress


@login_required
def competences_list(request):
    """Vue des compétences avec progression utilisateur."""
    skills = Skill.objects.all()
    skill_data = []
    for skill in skills:
        progress, _ = UserSkillProgress.objects.get_or_create(
            user=request.user, skill=skill,
            defaults={'unlocked': not skill.is_premium}
        )
        skill_data.append({
            'skill': skill,
            'progress': progress,
            'resources_count': skill.resources.count(),
        })

    # Score compétence global
    all_progress = UserSkillProgress.objects.filter(user=request.user)
    total = all_progress.count()
    if total > 0:
        global_score = sum(p.progress_percent for p in all_progress) / total
    else:
        global_score = 0

    context = {
        'skill_data': skill_data,
        'global_score': round(global_score),
    }
    return render(request, 'competences/competences.html', context)


@login_required
def apprentissage_view(request, slug):
    """Page d'apprentissage pour une compétence — tutoriels, PDFs, liens."""
    skill = get_object_or_404(Skill, slug=slug)
    progress, _ = UserSkillProgress.objects.get_or_create(
        user=request.user, skill=skill,
        defaults={'unlocked': not skill.is_premium}
    )

    # Vérifier accès
    if skill.is_premium and not progress.unlocked:
        messages.warning(request, f'Vous devez débloquer la compétence "{skill.name}" pour accéder aux ressources.')
        return redirect('payments:pay', item_type='skill', item_id=skill.id)

    # Récupérer toutes les ressources avec le statut de completion
    resources = skill.resources.all()
    resource_data = []
    for res in resources:
        user_progress, _ = UserResourceProgress.objects.get_or_create(
            user=request.user, resource=res
        )
        resource_data.append({
            'resource': res,
            'user_progress': user_progress,
        })

    # Stats
    total_resources = resources.count()
    completed_count = UserResourceProgress.objects.filter(
        user=request.user, resource__skill=skill, completed=True
    ).count()
    completion_pct = round((completed_count / total_resources * 100)) if total_resources > 0 else 0

    # Filtrage par type
    active_filter = request.GET.get('type', 'all')

    context = {
        'skill': skill,
        'progress': progress,
        'resource_data': resource_data,
        'total_resources': total_resources,
        'completed_count': completed_count,
        'completion_pct': completion_pct,
        'active_filter': active_filter,
    }
    return render(request, 'competences/apprentissage.html', context)


@login_required
def resource_detail_view(request, slug, resource_id):
    """Vue détaillée d'une ressource — tutoriel, PDF viewer, liens."""
    skill = get_object_or_404(Skill, slug=slug)
    resource = get_object_or_404(SkillResource, id=resource_id, skill=skill)
    progress, _ = UserSkillProgress.objects.get_or_create(
        user=request.user, skill=skill,
        defaults={'unlocked': not skill.is_premium}
    )

    # Vérifier accès (sauf aperçu gratuit)
    if skill.is_premium and not progress.unlocked and not resource.is_free_preview:
        messages.warning(request, 'Débloquons cette compétence d\'abord !')
        return redirect('payments:pay', item_type='skill', item_id=skill.id)

    user_progress, _ = UserResourceProgress.objects.get_or_create(
        user=request.user, resource=resource
    )

    context = {
        'skill': skill,
        'resource': resource,
        'progress': progress,
        'user_progress': user_progress,
    }
    return render(request, 'competences/resource_detail.html', context)


@login_required
def complete_resource(request, slug, resource_id):
    """Marquer une ressource comme terminée et gagner des XP."""
    skill = get_object_or_404(Skill, slug=slug)
    resource = get_object_or_404(SkillResource, id=resource_id, skill=skill)

    user_progress, _ = UserResourceProgress.objects.get_or_create(
        user=request.user, resource=resource
    )

    if not user_progress.completed:
        user_progress.completed = True
        user_progress.completed_at = timezone.now()
        user_progress.save()

        # Gagner des XP
        from gamification.models import XPEvent
        XPEvent.objects.create(
            user=request.user,
            action=f'resource_completed:{resource.title}',
            xp_earned=resource.xp_reward
        )
        request.user.total_xp += resource.xp_reward
        request.user.save()

        # Recalculer progression compétence
        skill_progress, _ = UserSkillProgress.objects.get_or_create(
            user=request.user, skill=skill,
            defaults={'unlocked': not skill.is_premium}
        )
        skill_progress.recalculate_progress()

        # Notification
        from notifications.models import Notification
        Notification.objects.create(
            user=request.user,
            title='Ressource terminée ! 🎓',
            message=f'Vous avez terminé "{resource.title}" et gagné {resource.xp_reward} XP.',
            notification_type='achievement',
            link=f'/competences/{slug}/'
        )

        messages.success(request, f'✅ Ressource terminée ! +{resource.xp_reward} XP')
    else:
        messages.info(request, 'Vous avez déjà terminé cette ressource.')

    return redirect('competences:apprentissage', slug=slug)
