from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class MedicalHistory(models.Model):
    """
    Hasta sağlık geçmişi modeli. Kronik hastalıklar, geçmiş ameliyatlar, alerjiler gibi
    bilgileri içerir.
    """
    CONDITION_TYPE_CHOICES = [
        ('chronic', _('Kronik Hastalık')),
        ('surgery', _('Geçirilmiş Ameliyat')),
        ('allergy', _('Alerji')),
        ('medication', _('Düzenli İlaç Kullanımı')),
        ('other', _('Diğer')),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_history',
        verbose_name=_('Hasta'),
        limit_choices_to={'user_type': 'patient'}
    )
    condition_type = models.CharField(
        max_length=20,
        choices=CONDITION_TYPE_CHOICES,
        verbose_name=_('Durum Tipi')
    )
    condition_name = models.CharField(
        max_length=200,
        verbose_name=_('Durum Adı/Tanımı')
    )
    diagnosed_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Tanı Tarihi')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Ek Notlar')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif mi?')
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
        verbose_name = _('Sağlık Geçmişi Kaydı')
        verbose_name_plural = _('Sağlık Geçmişi Kayıtları')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient} - {self.get_condition_type_display()}: {self.condition_name}"
