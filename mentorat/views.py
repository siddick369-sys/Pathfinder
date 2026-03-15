from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import MentorProfile, MentorSession, MentorReview, StudyGroup, StudyGroupMember
from notifications.models import Notification


@login_required
def mentors_list(request):
    """Liste des mentors disponibles."""
    mentors = MentorProfile.objects.filter(is_available=True).select_related('user')
    specialty = request.GET.get('specialty', '')
    university = request.GET.get('university', '')

    if specialty:
        mentors = [m for m in mentors if specialty.lower() in str(m.specialties).lower()]
    if university:
        mentors = mentors.filter(university__icontains=university)

    # Récupérer les universités uniques pour le filtre
    all_mentors = MentorProfile.objects.filter(is_available=True)
    universities = sorted(set(m.university for m in all_mentors if m.university))

    # Vérifier si l'utilisateur peut devenir mentor
    can_become_mentor = request.user.level >= 4
    is_mentor = hasattr(request.user, 'mentor_profile')

    context = {
        'mentors': mentors,
        'universities': universities,
        'active_specialty': specialty,
        'active_university': university,
        'can_become_mentor': can_become_mentor,
        'is_mentor': is_mentor,
    }
    return render(request, 'mentorat/list.html', context)


@login_required
def mentor_detail(request, pk):
    """Détail d'un profil mentor."""
    profile = get_object_or_404(MentorProfile, pk=pk)
    reviews = MentorReview.objects.filter(session__mentor=profile).select_related('reviewer').order_by('-created_at')[:10]
    groups = StudyGroup.objects.filter(mentor=profile, is_active=True)

    # Vérifier si une session découverte a déjà été utilisée
    has_free_intro = MentorSession.objects.filter(
        mentor=profile, mentee=request.user, is_free_intro=True
    ).exists()

    context = {
        'profile': profile,
        'reviews': reviews,
        'groups': groups,
        'has_free_intro': has_free_intro,
    }
    return render(request, 'mentorat/detail.html', context)


@login_required
def become_mentor(request):
    """Devenir mentor (Level 4+ requis)."""
    if request.user.level < 4:
        messages.warning(request, 'Vous devez atteindre le niveau 4 (Confirmé) pour devenir mentor.')
        return redirect('mentorat:list')

    if hasattr(request.user, 'mentor_profile'):
        messages.info(request, 'Vous êtes déjà mentor !')
        return redirect('mentorat:my_profile')

    if request.method == 'POST':
        bio = request.POST.get('bio', '').strip()
        specialties_raw = request.POST.get('specialties', '').strip()
        university = request.POST.get('university', '').strip()
        rate = request.POST.get('hourly_rate_fcfa', '500')

        if not bio:
            messages.error(request, 'Veuillez remplir votre présentation.')
            return render(request, 'mentorat/become_mentor.html')

        specialties = [s.strip() for s in specialties_raw.split(',') if s.strip()]

        MentorProfile.objects.create(
            user=request.user,
            bio=bio,
            specialties=specialties,
            university=university,
            hourly_rate_fcfa=int(rate) if rate.isdigit() else 500,
        )
        request.user.add_xp(100, action='devenu_mentor')
        Notification.objects.create(
            user=request.user,
            title='Vous êtes mentor ! 🎓',
            message='Votre profil mentor a été créé. Les étudiants peuvent maintenant réserver des sessions avec vous.',
            notification_type='achievement',
            link='/mentorat/mon-profil/'
        )
        messages.success(request, 'Félicitations ! Vous êtes maintenant mentor ! +100 XP')
        return redirect('mentorat:my_profile')

    return render(request, 'mentorat/become_mentor.html')


@login_required
def my_mentor_profile(request):
    """Mon profil mentor et mes sessions."""
    if not hasattr(request.user, 'mentor_profile'):
        return redirect('mentorat:become_mentor')

    profile = request.user.mentor_profile
    sessions = MentorSession.objects.filter(mentor=profile).select_related('mentee').order_by('-date')[:20]
    groups = StudyGroup.objects.filter(mentor=profile)

    context = {
        'profile': profile,
        'sessions': sessions,
        'groups': groups,
    }
    return render(request, 'mentorat/my_profile.html', context)


@login_required
def book_session(request, mentor_id):
    """Réserver une session de mentorat."""
    profile = get_object_or_404(MentorProfile, pk=mentor_id)

    if profile.user == request.user:
        messages.error(request, 'Vous ne pouvez pas réserver une session avec vous-même.')
        return redirect('mentorat:detail', pk=mentor_id)

    has_free_intro = MentorSession.objects.filter(
        mentor=profile, mentee=request.user, is_free_intro=True
    ).exists()

    if request.method == 'POST':
        session_type = request.POST.get('session_type', 'chat')
        date = request.POST.get('date', '')
        time_slot = request.POST.get('time_slot', '')
        topic = request.POST.get('topic', '')
        is_free = request.POST.get('is_free_intro') == 'on' and not has_free_intro

        price = 0 if is_free else profile.hourly_rate_fcfa

        session = MentorSession.objects.create(
            mentor=profile,
            mentee=request.user,
            session_type=session_type,
            date=date,
            time_slot=time_slot,
            topic=topic,
            price_fcfa=price,
            is_free_intro=is_free,
        )

        # Notifications
        Notification.objects.create(
            user=profile.user,
            title='Nouvelle session réservée ! 📅',
            message=f'{request.user.first_name} a réservé une session le {date} à {time_slot}.',
            notification_type='info',
            link='/mentorat/mon-profil/'
        )
        request.user.add_xp(20, action='session_mentorat_reservee')
        messages.success(request, 'Session réservée avec succès ! +20 XP')
        return redirect('mentorat:my_sessions')

    context = {
        'profile': profile,
        'has_free_intro': has_free_intro,
    }
    return render(request, 'mentorat/book_session.html', context)


@login_required
def my_sessions(request):
    """Mes sessions (en tant que mentoré)."""
    sessions = MentorSession.objects.filter(mentee=request.user).select_related('mentor__user').order_by('-date')
    context = {'sessions': sessions}
    return render(request, 'mentorat/my_sessions.html', context)


@login_required
def complete_session(request, session_id):
    """Marquer une session comme terminée et laisser un avis."""
    session = get_object_or_404(MentorSession, pk=session_id)

    if request.user != session.mentor.user and request.user != session.mentee:
        messages.error(request, 'Action non autorisée.')
        return redirect('mentorat:my_sessions')

    if request.method == 'POST':
        session.status = 'completed'
        session.save(update_fields=['status'])

        # Mettre à jour le compteur du mentor
        profile = session.mentor
        profile.total_sessions += 1
        profile.save(update_fields=['total_sessions'])

        # XP pour les deux participants
        session.mentor.user.add_xp(50, action='session_mentorat_completee')
        session.mentee.add_xp(30, action='session_mentorat_suivie')

        # Laisser un avis si c'est le mentoré
        if request.user == session.mentee:
            rating = int(request.POST.get('rating', 5))
            comment = request.POST.get('comment', '')
            rating = max(1, min(5, rating))
            MentorReview.objects.create(
                session=session,
                reviewer=request.user,
                rating=rating,
                comment=comment,
            )

        messages.success(request, 'Session terminée ! XP gagné !')
        return redirect('mentorat:my_sessions')

    context = {'session': session}
    return render(request, 'mentorat/complete_session.html', context)


@login_required
def join_group(request, group_id):
    """Rejoindre un groupe d'étude."""
    group = get_object_or_404(StudyGroup, pk=group_id, is_active=True)

    if group.is_full:
        messages.error(request, 'Ce groupe est complet.')
        return redirect('mentorat:detail', pk=group.mentor.pk)

    if StudyGroupMember.objects.filter(group=group, user=request.user).exists():
        messages.info(request, 'Vous êtes déjà membre de ce groupe.')
        return redirect('mentorat:detail', pk=group.mentor.pk)

    StudyGroupMember.objects.create(group=group, user=request.user)
    request.user.add_xp(25, action='groupe_etude_rejoint')

    Notification.objects.create(
        user=group.mentor.user,
        title='Nouveau membre ! 👥',
        message=f'{request.user.first_name} a rejoint votre groupe "{group.title}".',
        notification_type='info',
    )
    messages.success(request, f'Vous avez rejoint le groupe "{group.title}" ! +25 XP')
    return redirect('mentorat:detail', pk=group.mentor.pk)
