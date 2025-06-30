from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class UserThemePreference(models.Model):
    THEME_CHOICES = [
        ('light', _('Açık Tema')),
        ('dark', _('Koyu Tema')),
        ('system', _('Sistem Teması')),
    ]
    
    SIDEBAR_MODE_CHOICES = [
        ('light', _('Açık Kenar Çubuğu')),
        ('dark', _('Koyu Kenar Çubuğu')),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='theme_preference')
    dark_mode = models.BooleanField(default=False)
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='light',
        verbose_name=_('Tema')
    )
    sidebar_mode = models.CharField(
        max_length=20,
        choices=SIDEBAR_MODE_CHOICES,
        default='light',
        verbose_name=_('Kenar Çubuğu Modu')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s theme preference"
