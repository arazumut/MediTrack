from core.models_communication import CommunicationNotification
from core.models_theme import UserThemePreference

def notifications_processor(request):
    """
    Kullanıcının okunmamış bildirimlerini içerik işleyicisine ekler.
    """
    context = {}
    
    if request.user.is_authenticated:
        unread_notifications_count = CommunicationNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        # Son 5 bildirimi al
        recent_notifications = CommunicationNotification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        context['unread_notifications_count'] = unread_notifications_count
        context['recent_notifications'] = recent_notifications
    
    return context

def theme_processor(request):
    """
    Kullanıcının tema tercihini içerik işleyicisine ekler.
    """
    context = {}
    
    if request.user.is_authenticated:
        theme_preference, created = UserThemePreference.objects.get_or_create(user=request.user)
        context['dark_mode'] = theme_preference.dark_mode
    
    return context
