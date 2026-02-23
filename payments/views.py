from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import PaymentSimulation, UserProgress
from parcours.models import CareerStep
from competences.models import Skill, UserSkillProgress
from gamification.models import Booster, UserBooster
from notifications.models import Notification


@login_required
def payment_view(request, item_type, item_id):
    """
    Vue de paiement simulé.
    item_type: 'step', 'skill', ou 'booster'
    """
    item = None
    amount = 0
    title = ''

    if item_type == 'step':
        item = get_object_or_404(CareerStep, id=item_id)
        amount = item.price_fcfa
        title = item.title
    elif item_type == 'skill':
        item = get_object_or_404(Skill, id=item_id)
        amount = item.price_fcfa
        title = item.name
    elif item_type == 'booster':
        item = get_object_or_404(Booster, id=item_id)
        amount = item.price_fcfa
        title = item.name

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'mobile_money')
        phone = request.POST.get('phone', '')
        holder = request.POST.get('holder_name', '')

        # Créer la simulation de paiement
        payment_kwargs = {
            'user': request.user,
            'amount_fcfa': amount,
            'payment_method': method,
            'phone_number': phone,
            'holder_name': holder,
            'status': 'completed',
        }
        if item_type == 'step':
            payment_kwargs['step'] = item
        elif item_type == 'skill':
            payment_kwargs['skill'] = item
        elif item_type == 'booster':
            payment_kwargs['booster'] = item

        PaymentSimulation.objects.create(**payment_kwargs)

        # Déblocage
        if item_type == 'step':
            progress, _ = UserProgress.objects.get_or_create(user=request.user)
            progress.unlocked_steps.add(item)
            progress.recalculate()
            request.user.add_xp(50, action=f'etape_debloquee:{item.title}')

        elif item_type == 'skill':
            skill_progress, _ = UserSkillProgress.objects.get_or_create(
                user=request.user, skill=item
            )
            skill_progress.unlocked = True
            skill_progress.save()
            request.user.add_xp(50, action=f'competence_debloquee:{item.name}')

        elif item_type == 'booster':
            expires = None
            if item.duration_days > 0:
                expires = timezone.now() + timedelta(days=item.duration_days)
            UserBooster.objects.create(
                user=request.user, booster=item, expires_at=expires
            )
            request.user.add_xp(30, action=f'booster_active:{item.name}')

        # Notification
        Notification.objects.create(
            user=request.user,
            title=f'Paiement confirmé !',
            message=f'"{title}" a été débloqué avec succès pour {amount} FCFA.',
            notification_type='success',
        )

        return redirect('payments:confirmation')

    context = {
        'item_type': item_type,
        'item': item,
        'amount': amount,
        'title': title,
    }
    return render(request, 'payments/paiement.html', context)


@login_required
def confirmation_view(request):
    """Confirmation de paiement."""
    last_payment = PaymentSimulation.objects.filter(user=request.user).first()
    return render(request, 'payments/confirmation.html', {'payment': last_payment})
