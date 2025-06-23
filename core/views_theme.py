from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from core.models_theme import UserThemePreference

@login_required
@require_POST
@ensure_csrf_cookie
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
@ensure_csrf_cookie
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
