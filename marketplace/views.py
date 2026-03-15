from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import ServiceCategory, ServiceListing, Mission, MissionProposal, ServiceReview
from notifications.models import Notification


@login_required
def marketplace_home(request):
    """Page d'accueil de la marketplace."""
    categories = ServiceCategory.objects.all()
    listings = ServiceListing.objects.filter(status='active').select_related('provider', 'category')[:12]
    missions = Mission.objects.filter(status='open').select_related('client', 'category')[:6]

    cat_slug = request.GET.get('cat', '')
    if cat_slug:
        listings = listings.filter(category__slug=cat_slug)

    context = {
        'categories': categories,
        'listings': listings,
        'missions': missions,
        'active_cat': cat_slug,
    }
    return render(request, 'marketplace/home.html', context)


@login_required
def listing_detail(request, pk):
    """Détail d'une offre de service."""
    listing = get_object_or_404(ServiceListing, pk=pk)
    reviews = ServiceReview.objects.filter(listing=listing).select_related('reviewer').order_by('-created_at')[:10]
    context = {
        'listing': listing,
        'reviews': reviews,
    }
    return render(request, 'marketplace/listing_detail.html', context)


@login_required
def create_listing(request):
    """Créer une offre de service."""
    categories = ServiceCategory.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price_fcfa', '0')
        category_id = request.POST.get('category', '')
        delivery = request.POST.get('delivery_days', '3')

        if not title or not description:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'marketplace/create_listing.html', {'categories': categories})

        listing = ServiceListing.objects.create(
            provider=request.user,
            category_id=int(category_id) if category_id else None,
            title=title,
            description=description,
            price_fcfa=int(price) if price.isdigit() else 0,
            delivery_days=delivery,
        )
        request.user.add_xp(30, action='offre_service_creee')
        messages.success(request, 'Offre publiée avec succès ! +30 XP')
        return redirect('marketplace:listing_detail', pk=listing.pk)

    context = {'categories': categories}
    return render(request, 'marketplace/create_listing.html', context)


@login_required
def missions_list(request):
    """Liste des missions ouvertes."""
    missions = Mission.objects.filter(status='open').select_related('client', 'category')
    categories = ServiceCategory.objects.all()
    cat_slug = request.GET.get('cat', '')
    if cat_slug:
        missions = missions.filter(category__slug=cat_slug)

    context = {
        'missions': missions,
        'categories': categories,
        'active_cat': cat_slug,
    }
    return render(request, 'marketplace/missions.html', context)


@login_required
def mission_detail(request, pk):
    """Détail d'une mission."""
    mission = get_object_or_404(Mission, pk=pk)
    proposals = mission.proposals.select_related('provider').all()
    user_proposal = MissionProposal.objects.filter(mission=mission, provider=request.user).first()

    context = {
        'mission': mission,
        'proposals': proposals if request.user == mission.client else None,
        'user_proposal': user_proposal,
    }
    return render(request, 'marketplace/mission_detail.html', context)


@login_required
def create_mission(request):
    """Poster une mission."""
    categories = ServiceCategory.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        budget = request.POST.get('budget_fcfa', '0')
        category_id = request.POST.get('category', '')
        deadline = request.POST.get('deadline', '')

        if not title or not description or not deadline:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'marketplace/create_mission.html', {'categories': categories})

        mission = Mission.objects.create(
            client=request.user,
            category_id=int(category_id) if category_id else None,
            title=title,
            description=description,
            budget_fcfa=int(budget) if budget.isdigit() else 0,
            deadline=deadline,
        )
        request.user.add_xp(20, action='mission_postee')
        messages.success(request, 'Mission publiée ! +20 XP')
        return redirect('marketplace:mission_detail', pk=mission.pk)

    context = {'categories': categories}
    return render(request, 'marketplace/create_mission.html', context)


@login_required
def apply_mission(request, pk):
    """Postuler à une mission."""
    mission = get_object_or_404(Mission, pk=pk, status='open')

    if request.user == mission.client:
        messages.error(request, 'Vous ne pouvez pas postuler à votre propre mission.')
        return redirect('marketplace:mission_detail', pk=pk)

    if MissionProposal.objects.filter(mission=mission, provider=request.user).exists():
        messages.info(request, 'Vous avez déjà postulé à cette mission.')
        return redirect('marketplace:mission_detail', pk=pk)

    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        proposed_price = request.POST.get('proposed_price_fcfa', '0')

        MissionProposal.objects.create(
            mission=mission,
            provider=request.user,
            message=message_text,
            proposed_price_fcfa=int(proposed_price) if proposed_price.isdigit() else mission.budget_fcfa,
        )
        Notification.objects.create(
            user=mission.client,
            title='Nouvelle candidature ! 📩',
            message=f'{request.user.first_name} a postulé pour "{mission.title}".',
            notification_type='info',
            link=f'/marketplace/mission/{mission.pk}/'
        )
        request.user.add_xp(15, action='candidature_mission')
        messages.success(request, 'Candidature envoyée ! +15 XP')
        return redirect('marketplace:mission_detail', pk=pk)

    context = {'mission': mission}
    return render(request, 'marketplace/apply_mission.html', context)


@login_required
def accept_proposal(request, proposal_id):
    """Accepter une candidature (client uniquement)."""
    proposal = get_object_or_404(MissionProposal, pk=proposal_id)
    mission = proposal.mission

    if request.user != mission.client:
        messages.error(request, 'Action non autorisée.')
        return redirect('marketplace:mission_detail', pk=mission.pk)

    proposal.status = 'accepted'
    proposal.save(update_fields=['status'])

    mission.status = 'in_progress'
    mission.assigned_to = proposal.provider
    mission.save(update_fields=['status', 'assigned_to'])

    # Rejeter les autres candidatures
    MissionProposal.objects.filter(mission=mission).exclude(pk=proposal.pk).update(status='rejected')

    Notification.objects.create(
        user=proposal.provider,
        title='Candidature acceptée ! 🎉',
        message=f'Votre candidature pour "{mission.title}" a été acceptée !',
        notification_type='success',
        link=f'/marketplace/mission/{mission.pk}/'
    )
    proposal.provider.add_xp(50, action='candidature_acceptee')
    messages.success(request, f'Candidature de {proposal.provider.first_name} acceptée !')
    return redirect('marketplace:mission_detail', pk=mission.pk)


@login_required
def complete_mission(request, pk):
    """Marquer une mission comme terminée et laisser un avis."""
    mission = get_object_or_404(Mission, pk=pk, status='in_progress')

    if request.user != mission.client:
        messages.error(request, 'Action non autorisée.')
        return redirect('marketplace:mission_detail', pk=pk)

    if request.method == 'POST':
        mission.status = 'completed'
        mission.save(update_fields=['status'])

        rating = int(request.POST.get('rating', 5))
        rating = max(1, min(5, rating))
        comment = request.POST.get('comment', '')

        ServiceReview.objects.create(
            mission=mission,
            reviewer=request.user,
            provider=mission.assigned_to,
            rating=rating,
            comment=comment,
        )

        mission.assigned_to.add_xp(75, action='mission_completee')
        request.user.add_xp(20, action='mission_validee_client')

        Notification.objects.create(
            user=mission.assigned_to,
            title='Mission terminée ! 🏆',
            message=f'La mission "{mission.title}" est terminée. +75 XP !',
            notification_type='achievement',
        )
        messages.success(request, 'Mission terminée avec succès !')
        return redirect('marketplace:mission_detail', pk=pk)

    context = {'mission': mission}
    return render(request, 'marketplace/complete_mission.html', context)


@login_required
def my_services(request):
    """Mes offres de services et missions."""
    listings = ServiceListing.objects.filter(provider=request.user)
    posted_missions = Mission.objects.filter(client=request.user)
    assigned_missions = Mission.objects.filter(assigned_to=request.user)
    proposals = MissionProposal.objects.filter(provider=request.user).select_related('mission')

    context = {
        'listings': listings,
        'posted_missions': posted_missions,
        'assigned_missions': assigned_missions,
        'proposals': proposals,
    }
    return render(request, 'marketplace/my_services.html', context)
