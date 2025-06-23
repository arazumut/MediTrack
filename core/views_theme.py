from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from core.models_theme import UserThemePreference

@login_required
def toggle_theme(request):
    """
    View for toggling between dark and light mode
    """
    user = request.user
    
    # Get or create user theme preference
    theme_preference, created = UserThemePreference.objects.get_or_create(user=user)
    
    # Toggle the theme preference
    theme_preference.dark_mode = not theme_preference.dark_mode
    theme_preference.save()
    
    return JsonResponse({
        'success': True, 
        'dark_mode': theme_preference.dark_mode
    })

@login_required
def get_theme_preference(request):
    """
    View to get the current theme preference
    """
    user = request.user
    
    # Get or create user theme preference
    theme_preference, created = UserThemePreference.objects.get_or_create(user=user)
    
    return JsonResponse({
        'dark_mode': theme_preference.dark_mode
    })
