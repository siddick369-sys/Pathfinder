def global_context(request):
    """Context processor : fournit données globales à tous les templates."""
    context = {}
    if request.user.is_authenticated:
        from notifications.models import Notification
        context['unread_notifications_count'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        context['user_level_name'] = request.user.level_name
        context['user_level_icon'] = request.user.level_icon
    return context
