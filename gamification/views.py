from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Booster, UserBooster, UserBadge, XPEvent, Challenge, UserChallenge


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
    """Classement des utilisateurs par XP."""
    from accounts.models import CustomUser
    users = CustomUser.objects.filter(is_active=True, is_staff=False).order_by('-total_xp')[:20]
    context = {'leaderboard': users, 'current_user': request.user}
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

    context = {
        'badges': badges,
        'locked_badges': locked_badges,
        'xp_history': xp_history,
        'challenge_data': challenge_data,
        'xp_progress_pct': xp_progress_pct,
        'current_level_xp': current_level_xp,
        'next_level_xp': next_level_xp,
    }
    return render(request, 'gamification/profile.html', context)
