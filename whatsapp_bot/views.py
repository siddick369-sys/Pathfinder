import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import WhatsAppSubscriber, MicroLesson, WhatsAppMessage, ShareableResult
from orientation.models import OrientationResult


@login_required
def whatsapp_dashboard(request):
    """Dashboard WhatsApp — inscription et gestion."""
    subscriber = WhatsAppSubscriber.objects.filter(user=request.user).first()
    lessons = MicroLesson.objects.filter(is_active=True)[:5]

    # Stats
    total_subscribers = WhatsAppSubscriber.objects.filter(is_active=True).count()
    total_premium = WhatsAppSubscriber.objects.filter(is_premium=True).count()

    context = {
        'subscriber': subscriber,
        'lessons_preview': lessons,
        'total_subscribers': total_subscribers,
        'total_premium': total_premium,
    }
    return render(request, 'whatsapp_bot/dashboard.html', context)


@login_required
def subscribe_whatsapp(request):
    """S'inscrire aux notifications WhatsApp."""
    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        if not phone:
            messages.error(request, 'Veuillez entrer votre numéro WhatsApp.')
            return redirect('whatsapp:dashboard')

        subscriber, created = WhatsAppSubscriber.objects.get_or_create(
            phone_number=phone,
            defaults={
                'user': request.user,
                'name': f'{request.user.first_name} {request.user.last_name}',
            }
        )
        if not created and subscriber.user != request.user:
            messages.error(request, 'Ce numéro est déjà utilisé par un autre compte.')
            return redirect('whatsapp:dashboard')

        if created:
            request.user.add_xp(20, action='inscription_whatsapp')
            messages.success(request, 'Inscrit aux notifications WhatsApp ! +20 XP')
        else:
            messages.info(request, 'Vous êtes déjà inscrit.')

        return redirect('whatsapp:dashboard')

    return redirect('whatsapp:dashboard')


@login_required
def toggle_whatsapp_settings(request):
    """Activer/désactiver les paramètres WhatsApp."""
    subscriber = get_object_or_404(WhatsAppSubscriber, user=request.user)

    if request.method == 'POST':
        subscriber.daily_lesson_enabled = request.POST.get('daily_lesson') == 'on'
        subscriber.reminder_enabled = request.POST.get('reminder') == 'on'
        subscriber.save(update_fields=['daily_lesson_enabled', 'reminder_enabled'])
        messages.success(request, 'Paramètres mis à jour.')

    return redirect('whatsapp:dashboard')


@login_required
def generate_share_result(request):
    """Générer un résultat partageable pour WhatsApp."""
    result = OrientationResult.objects.filter(user=request.user).first()
    if not result or not result.recommended_career:
        messages.error(request, 'Passez le test d\'orientation d\'abord !')
        return redirect('orientation:test')

    # Récupérer le meilleur score
    scores = result.scores
    best_slug = max(scores, key=scores.get) if scores else ''
    best_pct = scores.get(best_slug, 0)

    share_code = uuid.uuid4().hex[:12]
    shareable = ShareableResult.objects.create(
        user=request.user,
        career_name=result.recommended_career.title,
        match_percentage=best_pct,
        share_code=share_code,
    )
    request.user.add_xp(10, action='resultat_partage')
    messages.success(request, 'Lien de partage généré ! +10 XP')
    return redirect('whatsapp:share_page', code=share_code)


def share_page(request, code):
    """Page publique de partage d'un résultat."""
    shareable = get_object_or_404(ShareableResult, share_code=code)
    shareable.views_count += 1
    shareable.save(update_fields=['views_count'])

    context = {'result': shareable}
    return render(request, 'whatsapp_bot/share.html', context)


@login_required
def micro_lessons_list(request):
    """Liste des micro-leçons disponibles."""
    free_lessons = MicroLesson.objects.filter(is_active=True, level='free')
    premium_lessons = MicroLesson.objects.filter(is_active=True, level='premium')
    subscriber = WhatsAppSubscriber.objects.filter(user=request.user).first()
    is_premium = subscriber.is_premium if subscriber else False

    context = {
        'free_lessons': free_lessons,
        'premium_lessons': premium_lessons,
        'is_premium': is_premium,
    }
    return render(request, 'whatsapp_bot/lessons.html', context)


# --- API Endpoints pour intégration future avec WhatsApp Business API ---

@csrf_exempt
@require_POST
def webhook_receive(request):
    """Webhook pour recevoir les messages WhatsApp (prêt pour WhatsApp Business API)."""
    return JsonResponse({'status': 'ok', 'message': 'Webhook prêt pour intégration WhatsApp Business API'})
