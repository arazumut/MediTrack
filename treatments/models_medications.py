from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Medication(models.Model):
    """
    İlaç veritabanı. Tüm ilaçların bilgilerini içerir.
    """
    name = models.CharField(
        max_length=200,
        verbose_name=_('İlaç Adı')
    )
    active_ingredient = models.CharField(
        max_length=200,
        verbose_name=_('Etken Madde')
    )
    drug_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('İlaç Kodu')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    side_effects = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Yan Etkiler')
    )
    contraindications = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Kontrendikasyonlar')
    )
    is_prescription = models.BooleanField(
        default=True,
        verbose_name=_('Reçeteli mi?')
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
        verbose_name = _('İlaç')
        verbose_name_plural = _('İlaçlar')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.active_ingredient})"

class MedicationInteraction(models.Model):
    """
    İlaç etkileşimleri. İki ilaç arasındaki olası etkileşimleri tanımlar.
    """
    SEVERITY_CHOICES = [
        ('mild', _('Hafif')),
        ('moderate', _('Orta')),
        ('severe', _('Ciddi')),
    ]
    
    medication1 = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='interactions_as_first',
        verbose_name=_('İlaç 1')
    )
    medication2 = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='interactions_as_second',
        verbose_name=_('İlaç 2')
    )
    description = models.TextField(
        verbose_name=_('Etkileşim Açıklaması')
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        verbose_name=_('Şiddet')
    )
    recommendations = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Öneriler')
    )
    
    class Meta:
        verbose_name = _('İlaç Etkileşimi')
        verbose_name_plural = _('İlaç Etkileşimleri')
        unique_together = [['medication1', 'medication2']]
        
    def __str__(self):
        return f"{self.medication1.name} - {self.medication2.name} ({self.get_severity_display()})"

# treatments/models.py dosyasında bulunan Prescription modeline eklenecek alanlar:
# from treatments.models_medications import Medication

# class Prescription(models.Model):
#     ...
#     medication = models.ForeignKey(
#         Medication,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='prescriptions',
#         verbose_name=_('İlaç')
#     )
#     ...
