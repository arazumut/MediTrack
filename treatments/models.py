from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from appointments.models import Appointment

class Treatment(models.Model):
    """
    Tedavi modeli, bir randevu sonucunda doktor tarafından hastaya uygulanan tedavi bilgilerini içerir.
    """
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='treatment',
        verbose_name=_('Randevu')
    )
    diagnosis = models.TextField(
        verbose_name=_('Teşhis')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notlar')
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
        verbose_name = _('Tedavi')
        verbose_name_plural = _('Tedaviler')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.appointment.patient} - {self.diagnosis[:30]}"

class Prescription(models.Model):
    """
    Reçete modeli, bir tedavi için verilen ilaç bilgilerini içerir.
    """
    treatment = models.ForeignKey(
        Treatment,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name=_('Tedavi')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('İlaç Adı')
    )
    medication = models.ForeignKey(
        'treatments.Medication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions',
        verbose_name=_('İlaç')
    )
    dosage = models.CharField(
        max_length=100,
        verbose_name=_('Doz')
    )
    instructions = models.TextField(
        verbose_name=_('Kullanım Talimatları')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        verbose_name = _('Reçete')
        verbose_name_plural = _('Reçeteler')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.dosage}"

# Diğer modeller için import
from .models_medical_history import MedicalHistory
from .models_lab import LabTest, TestResult
from .models_medications import Medication, MedicationInteraction
from .models_imaging import MedicalImage, Report
