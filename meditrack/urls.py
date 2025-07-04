"""
URL configuration for meditrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from core.forms import LoginForm
from core.views import HomeView, dashboard
from core.logout_view import logout_view
from core.views_theme import toggle_theme, get_theme_preference

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Ana sayfa
    path('', HomeView.as_view(), name='home'),
    
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        authentication_form=LoginForm
    ), name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Tema ayarları
    path('theme/toggle/', toggle_theme, name='toggle-theme'),
    path('theme/preference/', get_theme_preference, name='get-theme-preference'),
    
    # Core uygulaması URL'leri
    path('core/', include('core.urls', namespace='core')),
    
    # Appointments uygulaması URL'leri
    path('appointments/', include('appointments.urls')),
    
    # Treatments uygulaması URL'leri
    path('treatments/', include('treatments.urls')),
    
    # Telemedicine uygulaması URL'leri
    path('telemedicine/', include('telemedicine.urls')),
]

# Media ve static dosyaları için URL'ler
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
