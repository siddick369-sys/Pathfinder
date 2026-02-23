from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from payments.models import UserProgress
from orientation.models import OrientationResult
from gamification.models import UserBadge, XPEvent
from notifications.models import Notification


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Créer la progression
            UserProgress.objects.create(user=user)
            # XP pour inscription
            user.add_xp(50, action='inscription_complete')
            # Notification bienvenue
            Notification.objects.create(
                user=user,
                title='Bienvenue sur PathFinder ! 🎉',
                message=f'Félicitations {user.first_name}, votre compte a été créé. Commencez par le test d\'orientation !',
                notification_type='success',
                link='/orientation/'
            )
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé avec succès.')
            return redirect('accounts:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/inscription.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # XP connexion quotidienne
                from django.utils import timezone
                today = timezone.now().date()
                already = XPEvent.objects.filter(user=user, action='connexion_quotidienne', created_at__date=today).exists()
                if not already:
                    user.add_xp(10, action='connexion_quotidienne')
                messages.success(request, f'Bon retour, {user.first_name} !')
                return redirect(request.GET.get('next', 'accounts:dashboard'))
            else:
                messages.error(request, 'Identifiant ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'accounts/connexion.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('core:home')


@login_required
def dashboard_view(request):
    user = request.user
    progress, _ = UserProgress.objects.get_or_create(user=user)

    # Dernier résultat orientation
    latest_result = OrientationResult.objects.filter(user=user).first()

    # Badges récents
    recent_badges = UserBadge.objects.filter(user=user).select_related('badge').order_by('-earned_at')[:5]

    # XP récents
    recent_xp = XPEvent.objects.filter(user=user)[:5]

    # Notifications non lues
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]

    # Étapes carrière si résultat existe
    career_steps = []
    recommended_career = None
    if latest_result and latest_result.recommended_career:
        recommended_career = latest_result.recommended_career
        steps = recommended_career.steps.all().order_by('order')
        for step in steps:
            is_completed = progress.completed_steps.filter(id=step.id).exists()
            is_unlocked = step.is_free or progress.unlocked_steps.filter(id=step.id).exists()
            career_steps.append({
                'step': step,
                'is_completed': is_completed,
                'is_unlocked': is_unlocked,
                'status': 'completed' if is_completed else ('unlocked' if is_unlocked else 'locked'),
            })

    context = {
        'progress': progress,
        'latest_result': latest_result,
        'recommended_career': recommended_career,
        'career_steps': career_steps,
        'recent_badges': recent_badges,
        'recent_xp': recent_xp,
        'notifications': notifications,
    }
    return render(request, 'accounts/dashboard.html', context)
