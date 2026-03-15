import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (Booster, UserBooster, UserBadge, XPEvent, Challenge, UserChallenge,
                     Referral, UserStreak, XPDiscount)


@login_required
def shop_view(request):
    """Boutique éthique."""
    boosters = Booster.objects.all()
    user_boosters = UserBooster.objects.filter(user=request.user, is_active=True)
    active_ids = [ub.booster_id for ub in user_boosters]

    booster_data = []
    for b in boosters:
        booster_data.append({
            'booster': b,
            'is_owned': b.id in active_ids,
        })

    context = {
        'booster_data': booster_data,
        'user_xp': request.user.total_xp,
    }
    return render(request, 'gamification/shop.html', context)


@login_required
def leaderboard_view(request):
    """Classement des utilisateurs par XP — avec classement par université."""
    from accounts.models import CustomUser
    users = CustomUser.objects.filter(is_active=True, is_staff=False).order_by('-total_xp')[:20]

    # Classement par université (via mentorat)
    from mentorat.models import MentorProfile
    university_rankings = {}
    for profile in MentorProfile.objects.all().select_related('user'):
        if profile.university:
            if profile.university not in university_rankings:
                university_rankings[profile.university] = {'total_xp': 0, 'count': 0}
            university_rankings[profile.university]['total_xp'] += profile.user.total_xp
            university_rankings[profile.university]['count'] += 1

    uni_ranking = sorted(
        [{'name': k, **v, 'avg_xp': v['total_xp'] // max(v['count'], 1)}
         for k, v in university_rankings.items()],
        key=lambda x: x['total_xp'], reverse=True
    )[:10]

    context = {
        'leaderboard': users,
        'current_user': request.user,
        'uni_ranking': uni_ranking,
    }
    return render(request, 'gamification/leaderboard.html', context)


@login_required
def profile_gamification(request):
    """Profil gamification de l'utilisateur."""
    from .models import Badge
    import math

    badges = UserBadge.objects.filter(user=request.user).select_related('badge')
    earned_ids = [ub.badge_id for ub in badges]
    locked_badges = Badge.objects.exclude(id__in=earned_ids)
    xp_history = XPEvent.objects.filter(user=request.user)[:20]
    active_challenges = Challenge.objects.filter(is_active=True)

    challenge_data = []
    for ch in active_challenges:
        uc = UserChallenge.objects.filter(user=request.user, challenge=ch).first()
        challenge_data.append({
            'challenge': ch,
            'participation': uc,
            'is_completed': uc.completed if uc else False,
        })

    # Calculate XP progress to next level
    user = request.user
    current_level_xp = int(100 * (user.level ** 1.5))
    next_level_xp = int(100 * ((user.level + 1) ** 1.5))
    xp_range = next_level_xp - current_level_xp
    xp_in_level = user.total_xp - current_level_xp
    xp_progress_pct = min(100, int((xp_in_level / max(xp_range, 1)) * 100))

    # Streak
    streak, _ = UserStreak.objects.get_or_create(user=request.user)

    # Referral code
    referral_code = f'PF{request.user.id:04d}'
    referrals_count = Referral.objects.filter(referrer=request.user).count()

    # XP discounts
    available_discounts = XPDiscount.objects.filter(user=request.user, is_used=False)

    context = {
        'badges': badges,
        'locked_badges': locked_badges,
        'xp_history': xp_history,
        'challenge_data': challenge_data,
        'xp_progress_pct': xp_progress_pct,
        'current_level_xp': current_level_xp,
        'next_level_xp': next_level_xp,
        'streak': streak,
        'referral_code': referral_code,
        'referrals_count': referrals_count,
        'available_discounts': available_discounts,
    }
    return render(request, 'gamification/profile.html', context)


@login_required
def convert_xp_to_discount(request):
    """Convertir 1000 XP en 500 FCFA de réduction."""
    XP_COST = 1000
    DISCOUNT_FCFA = 500

    if request.user.total_xp < XP_COST:
        messages.error(request, f'Vous avez besoin de {XP_COST} XP minimum. Vous avez {request.user.total_xp} XP.')
        return redirect('gamification:profile')

    # Déduire l'XP
    request.user.total_xp -= XP_COST
    request.user.save(update_fields=['total_xp'])

    # Créer la réduction
    discount = XPDiscount.objects.create(
        user=request.user,
        xp_spent=XP_COST,
        discount_fcfa=DISCOUNT_FCFA,
        discount_code=uuid.uuid4().hex[:10].upper(),
    )

    XPEvent.objects.create(user=request.user, action='conversion_xp_reduction', xp_earned=-XP_COST)

    messages.success(request, f'Réduction de {DISCOUNT_FCFA} FCFA obtenue ! Code : {discount.discount_code}')
    return redirect('gamification:profile')


@login_required
def referral_view(request):
    """Page de parrainage."""
    referral_code = f'PF{request.user.id:04d}'
    referrals = Referral.objects.filter(referrer=request.user).select_related('referred')

    context = {
        'referral_code': referral_code,
        'referrals': referrals,
        'total_xp_earned': referrals.count() * 50,
    }
    return render(request, 'gamification/referral.html', context)
