from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    """Oturum kapatıp login sayfasına yönlendiren özel view."""
    logout(request)
    return redirect('login')
