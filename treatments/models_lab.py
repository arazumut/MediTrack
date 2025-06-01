from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from treatments.models import Treatment

class LabTest(models.Model):
    """
    Laboratuvar testi modeli. Doktorlar tarafından istenen testleri temsil eder.
    """
    TEST_STATUS_CHOICES = [
        ('requested', _('Talep Edildi')),
        ('in_progress', _('İşlemde')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    treatment = models.ForeignKey(
        Treatment,
        on_delete=models.CASCADE,
        related_name='lab_tests',
        verbose_name=_('Tedavi')
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lab_tests',
        verbose_name=_('Hasta'),
        limit_choices_to={'user_type': 'patient'}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_lab_tests',
        verbose_name=_('İsteyen Doktor'),
        limit_choices_to={'user_type': 'doctor'}
    )
    test_name = models.CharField(
        max_length=200,
        verbose_name=_('Test Adı')
    )
    test_details = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Test Detayları')
    )
    status = models.CharField(
        max_length=20,
        choices=TEST_STATUS_CHOICES,
        default='requested',
        verbose_name=_('Durum')
    )
    requested_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('İstek Tarihi')
    )
    completed_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Tamamlanma Tarihi')
    )
    
    class Meta:
        verbose_name = _('Laboratuvar Testi')
        verbose_name_plural = _('Laboratuvar Testleri')
        ordering = ['-requested_date']
    
    def __str__(self):
        return f"{self.patient} - {self.test_name} - {self.get_status_display()}"

class TestResult(models.Model):
    """
    Test sonucu modeli. Bir laboratuvar testinin sonuçlarını temsil eder.
    """
    lab_test = models.OneToOneField(
        LabTest,
        on_delete=models.CASCADE,
        related_name='result',
        verbose_name=_('Laboratuvar Testi')
    )
    result_text = models.TextField(
        verbose_name=_('Sonuç Metni')
    )
    reference_values = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Referans Değerler')
    )
    is_normal = models.BooleanField(
        default=True,
        verbose_name=_('Normal mi?')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notlar')
    )
    technician = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Teknisyen/Laborant')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Güncellenme Tarihi')
    )
    result_file = models.FileField(
        upload_to='lab_results/',
        blank=True,
        null=True,
        verbose_name=_('Sonuç Dosyası')
    )
    
    class Meta:
        verbose_name = _('Test Sonucu')
        verbose_name_plural = _('Test Sonuçları')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.lab_test.test_name} - {self.lab_test.patient}"
    
    def save(self, *args, **kwargs):
        # Test sonucu eklendiğinde, laboratuvar testinin durumu "tamamlandı" olarak güncellenir
        if not self.pk:  # Yeni kayıt ise
            self.lab_test.status = 'completed'
            self.lab_test.completed_date = self.created_at
            self.lab_test.save()
        super().save(*args, **kwargs)
