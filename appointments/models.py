from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Appointment(models.Model):
    """
    Randevu modeli, hasta ve doktor arasındaki randevuları temsil eder.
    """
    STATUS_CHOICES = [
        ('planned', _('Planlandı')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='patient_appointments',
        verbose_name=_('Hasta'),
        limit_choices_to={'user_type': 'patient'}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_appointments',
        verbose_name=_('Doktor'),
        limit_choices_to={'user_type': 'doctor'}
    )
    date = models.DateField(
        verbose_name=_('Tarih')
    )
    time = models.TimeField(
        verbose_name=_('Saat')
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Açıklama')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name=_('Durum')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Güncellenme Tarihi')
    )
    
    class Meta:
        verbose_name = _('Randevu')
        verbose_name_plural = _('Randevular')
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.date} {self.time}"
