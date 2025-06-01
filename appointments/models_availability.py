from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import datetime

class DoctorAvailability(models.Model):
    """
    Doktor uygunluk takvimi. Doktorların hangi günlerde ve saatlerde 
    müsait olduğunu belirler.
    """
    WEEKDAY_CHOICES = [
        (0, _('Pazartesi')),
        (1, _('Salı')),
        (2, _('Çarşamba')),
        (3, _('Perşembe')),
        (4, _('Cuma')),
        (5, _('Cumartesi')),
        (6, _('Pazar')),
    ]
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities',
        verbose_name=_('Doktor'),
        limit_choices_to={'user_type': 'doctor'}
    )
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        verbose_name=_('Haftanın Günü')
    )
    start_time = models.TimeField(
        verbose_name=_('Başlangıç Saati')
    )
    end_time = models.TimeField(
        verbose_name=_('Bitiş Saati')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif mi?')
    )
    
    class Meta:
        verbose_name = _('Doktor Uygunluğu')
        verbose_name_plural = _('Doktor Uygunlukları')
        ordering = ['weekday', 'start_time']
        unique_together = ['doctor', 'weekday', 'start_time', 'end_time']
    
    def __str__(self):
        return f"{self.doctor} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"
    
    def get_weekday_name(self):
        return self.get_weekday_display()
    
    def is_available_on_date(self, date):
        """Belirli bir tarihte doktorun uygun olup olmadığını kontrol eder"""
        # Tarih, bu uygunluğun gününe denk geliyor mu?
        return date.weekday() == self.weekday and self.is_active

class DoctorTimeOff(models.Model):
    """
    Doktorların izin günleri/saatleri. Normalde müsait oldukları zamanlarda
    özel sebeplerle izinli oldukları zamanları belirtir.
    """
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_offs',
        verbose_name=_('Doktor'),
        limit_choices_to={'user_type': 'doctor'}
    )
    start_date = models.DateField(
        verbose_name=_('Başlangıç Tarihi')
    )
    end_date = models.DateField(
        verbose_name=_('Bitiş Tarihi')
    )
    start_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_('Başlangıç Saati'),
        help_text=_('Eğer tam gün izin değilse')
    )
    end_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_('Bitiş Saati'),
        help_text=_('Eğer tam gün izin değilse')
    )
    reason = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('İzin Sebebi')
    )
    is_full_day = models.BooleanField(
        default=True,
        verbose_name=_('Tam Gün mü?')
    )
    
    class Meta:
        verbose_name = _('Doktor İzni')
        verbose_name_plural = _('Doktor İzinleri')
        ordering = ['-start_date', '-start_time']
    
    def __str__(self):
        if self.is_full_day:
            return f"{self.doctor} - {self.start_date} - {self.end_date}"
        return f"{self.doctor} - {self.start_date} {self.start_time} - {self.end_date} {self.end_time}"
