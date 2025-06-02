from core.models_communication import Notification

def notifications_processor(request):
    """
    Kullanıcının okunmamış bildirimlerini içerik işleyicisine ekler.
    """
    context = {}
    
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        # Son 5 bildirimi al
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        context['unread_notifications_count'] = unread_notifications_count
        context['recent_notifications'] = recent_notifications
    
    return context
