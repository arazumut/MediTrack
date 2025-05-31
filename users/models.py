from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    MediTrack sistemi için özel kullanıcı modeli.
    Her kullanıcı hasta, doktor, resepsiyonist veya admin olabilir.
    """
    USER_TYPE_CHOICES = [
        ('patient', _('Hasta')),
        ('doctor', _('Doktor')),
        ('receptionist', _('Resepsiyonist')),
        ('admin', _('Admin')),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='patient',
        verbose_name=_('Kullanıcı Tipi')
    )
    
    # Doktorlar için ek alanlar
    specialization = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name=_('Uzmanlık Alanı')
    )
    
    # Hastalar için ek alanlar
    date_of_birth = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_('Doğum Tarihi')
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_('Telefon Numarası')
    )
    address = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Adres')
    )
    blood_type = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        verbose_name=_('Kan Grubu')
    )
    
    def is_patient(self):
        return self.user_type == 'patient'
    
    def is_doctor(self):
        return self.user_type == 'doctor'
    
    def is_receptionist(self):
        return self.user_type == 'receptionist'
    
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    class Meta:
        verbose_name = _('Kullanıcı')
        verbose_name_plural = _('Kullanıcılar')
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
