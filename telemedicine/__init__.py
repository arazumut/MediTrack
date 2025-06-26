"""
Telemedicine Module for MediTracked
Online consultation and video call system
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.validators import URLValidator
from appointments.models import Appointment
import uuid


class TeleMedicineConsultation(models.Model):
    """
    Uzaktan sağlık konsültasyonu modeli
    """
    CONSULTATION_TYPE_CHOICES = [
        ('video', _('Video Görüşme')),
        ('audio', _('Ses Görüşmesi')),
        ('chat', _('Metin Sohbeti')),
        ('hybrid', _('Karma (Video + Chat)')),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', _('Zamanlandı')),
        ('waiting', _('Bekleniyor')),
        ('in_progress', _('Devam Ediyor')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
        ('no_show', _('Katılım Sağlanmadı')),
        ('technical_issue', _('Teknik Sorun')),
    ]
    
    # Temel bilgiler
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='telemedicine_consultation',
        verbose_name=_('Randevu')
    )
    
    consultation_type = models.CharField(
        max_length=20,
        choices=CONSULTATION_TYPE_CHOICES,
        default='video',
        verbose_name=_('Konsültasyon Türü')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name=_('Durum')
    )
    
    # Video konferans bilgileri
    meeting_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name=_('Toplantı ID')
    )
    
    meeting_url = models.URLField(
        blank=True,
        verbose_name=_('Toplantı URL\'si'),
        help_text=_('Video konferans bağlantısı')
    )
    
    meeting_password = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Toplantı Şifresi')
    )
    
    # Platform bilgileri
    platform = models.CharField(
        max_length=50,
        choices=[
            ('zoom', 'Zoom'),
            ('teams', 'Microsoft Teams'),
            ('meet', 'Google Meet'),
            ('webex', 'Cisco Webex'),
            ('internal', 'Internal System'),
        ],
        default='internal',
        verbose_name=_('Platform')
    )
    
    # Zaman bilgileri
    scheduled_start_time = models.DateTimeField(
        verbose_name=_('Planlanan Başlangıç')
    )
    
    actual_start_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Gerçek Başlangıç')
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Bitiş Zamanı')
    )
    
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Süre (Dakika)')
    )
    
    # Katılımcı bilgileri
    doctor_joined_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Doktor Katılım Zamanı')
    )
    
    patient_joined_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Hasta Katılım Zamanı')
    )
    
    # Teknik detaylar
    connection_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', _('Mükemmel')),
            ('good', _('İyi')),
            ('fair', _('Orta')),
            ('poor', _('Kötü')),
        ],
        blank=True,
        verbose_name=_('Bağlantı Kalitesi')
    )
    
    technical_issues = models.TextField(
        blank=True,
        verbose_name=_('Teknik Sorunlar')
    )
    
    # Konsültasyon detayları
    consultation_notes = models.TextField(
        blank=True,
        verbose_name=_('Konsültasyon Notları')
    )
    
    patient_feedback = models.TextField(
        blank=True,
        verbose_name=_('Hasta Geri Bildirimi')
    )
    
    doctor_feedback = models.TextField(
        blank=True,
        verbose_name=_('Doktor Geri Bildirimi')
    )
    
    # Rating system
    patient_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name=_('Hasta Değerlendirmesi (1-5)')
    )
    
    doctor_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name=_('Doktor Değerlendirmesi (1-5)')
    )
    
    # Kayıt ve dosya paylaşımı
    is_recorded = models.BooleanField(
        default=False,
        verbose_name=_('Kayıt Yapıldı mı?')
    )
    
    recording_url = models.URLField(
        blank=True,
        verbose_name=_('Kayıt URL\'si')
    )
    
    shared_files = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Paylaşılan Dosyalar'),
        help_text=_('Konsültasyon sırasında paylaşılan dosya listesi')
    )
    
    # Güvenlik ve gizlilik
    is_encrypted = models.BooleanField(
        default=True,
        verbose_name=_('Şifreli mi?')
    )
    
    waiting_room_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Bekleme Odası Aktif')
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Güncellenme Tarihi')
    )
    
    class Meta:
        verbose_name = _('Telemedicine Konsültasyonu')
        verbose_name_plural = _('Telemedicine Konsültasyonları')
        ordering = ['-scheduled_start_time']
    
    def __str__(self):
        return f"{self.appointment.patient} - {self.appointment.doctor} - {self.scheduled_start_time}"
    
    def get_duration(self):
        """Konsültasyon süresini hesapla"""
        if self.actual_start_time and self.end_time:
            duration = self.end_time - self.actual_start_time
            return duration.total_seconds() / 60  # Dakika cinsinden
        return 0
    
    def is_active(self):
        """Konsültasyon aktif mi?"""
        return self.status == 'in_progress'
    
    def can_join(self, user):
        """Kullanıcı konsültasyona katılabilir mi?"""
        if self.status not in ['scheduled', 'waiting', 'in_progress']:
            return False
        
        # Sadece doktor ve hasta katılabilir
        return user in [self.appointment.doctor, self.appointment.patient]
    
    def get_join_url(self):
        """Katılım URL'sini oluştur"""
        if self.meeting_url:
            return self.meeting_url
        
        # Internal sistem için URL oluştur
        return f"/telemedicine/join/{self.meeting_id}/"
    
    def mark_as_started(self, user):
        """Konsültasyonu başlatıldı olarak işaretle"""
        if not self.actual_start_time:
            self.actual_start_time = timezone.now()
            self.status = 'in_progress'
        
        # Katılım zamanını kaydet
        if user == self.appointment.doctor:
            self.doctor_joined_at = timezone.now()
        elif user == self.appointment.patient:
            self.patient_joined_at = timezone.now()
        
        self.save()
    
    def mark_as_completed(self):
        """Konsültasyonu tamamlandı olarak işaretle"""
        if not self.end_time:
            self.end_time = timezone.now()
        
        self.status = 'completed'
        
        # Süreyi hesapla
        if self.actual_start_time:
            self.duration_minutes = int(self.get_duration())
        
        self.save()


class TeleMedicineMessage(models.Model):
    """
    Telemedicine chat mesajları
    """
    consultation = models.ForeignKey(
        TeleMedicineConsultation,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name=_('Konsültasyon')
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Gönderen')
    )
    
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', _('Metin')),
            ('file', _('Dosya')),
            ('image', _('Görsel')),
            ('system', _('Sistem Mesajı')),
        ],
        default='text',
        verbose_name=_('Mesaj Türü')
    )
    
    content = models.TextField(
        verbose_name=_('İçerik')
    )
    
    file_url = models.URLField(
        blank=True,
        verbose_name=_('Dosya URL\'si')
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Okundu mu?')
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Zaman Damgası')
    )
    
    class Meta:
        verbose_name = _('Telemedicine Mesajı')
        verbose_name_plural = _('Telemedicine Mesajları')
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender} - {self.timestamp}"


class TeleMedicineSettings(models.Model):
    """
    Telemedicine ayarları
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telemedicine_settings',
        verbose_name=_('Kullanıcı')
    )
    
    # Video ayarları
    default_camera_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Varsayılan Kamera Açık')
    )
    
    default_microphone_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Varsayılan Mikrofon Açık')
    )
    
    video_quality = models.CharField(
        max_length=20,
        choices=[
            ('low', _('Düşük (360p)')),
            ('medium', _('Orta (720p)')),
            ('high', _('Yüksek (1080p)')),
        ],
        default='medium',
        verbose_name=_('Video Kalitesi')
    )
    
    # Bildirim ayarları
    consultation_reminders = models.BooleanField(
        default=True,
        verbose_name=_('Konsültasyon Hatırlatmaları')
    )
    
    reminder_minutes_before = models.PositiveIntegerField(
        default=15,
        verbose_name=_('Kaç Dakika Önce Hatırlat')
    )
    
    email_notifications = models.BooleanField(
        default=True,
        verbose_name=_('E-posta Bildirimleri')
    )
    
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name=_('SMS Bildirimleri')
    )
    
    # Güvenlik ayarları
    require_waiting_room = models.BooleanField(
        default=True,
        verbose_name=_('Bekleme Odası Zorunlu')
    )
    
    allow_recording = models.BooleanField(
        default=False,
        verbose_name=_('Kayıt İzni')
    )
    
    allow_file_sharing = models.BooleanField(
        default=True,
        verbose_name=_('Dosya Paylaşım İzni')
    )
    
    # Gelişmiş ayarlar
    max_consultation_duration = models.PositiveIntegerField(
        default=60,
        verbose_name=_('Maksimum Konsültasyon Süresi (Dakika)')
    )
    
    auto_end_consultation = models.BooleanField(
        default=False,
        verbose_name=_('Otomatik Konsültasyon Sonu')
    )
    
    class Meta:
        verbose_name = _('Telemedicine Ayarları')
        verbose_name_plural = _('Telemedicine Ayarları')
    
    def __str__(self):
        return f"{self.user} - Telemedicine Ayarları"


class TeleMedicineAnalytics(models.Model):
    """
    Telemedicine kullanım analitikleri
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telemedicine_analytics',
        verbose_name=_('Kullanıcı')
    )
    
    date = models.DateField(
        verbose_name=_('Tarih')
    )
    
    # Günlük istatistikler
    total_consultations = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Toplam Konsültasyon')
    )
    
    completed_consultations = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Tamamlanan Konsültasyon')
    )
    
    cancelled_consultations = models.PositiveIntegerField(
        default=0,
        verbose_name=_('İptal Edilen Konsültasyon')
    )
    
    total_duration_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Toplam Süre (Dakika)')
    )
    
    average_duration_minutes = models.FloatField(
        default=0,
        verbose_name=_('Ortalama Süre (Dakika)')
    )
    
    # Teknik istatistikler
    connection_issues = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Bağlantı Sorunları')
    )
    
    technical_support_requests = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Teknik Destek Talepleri')
    )
    
    # Memnuniyet skorları
    average_patient_rating = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Ortalama Hasta Puanı')
    )
    
    average_doctor_rating = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Ortalama Doktor Puanı')
    )
    
    class Meta:
        verbose_name = _('Telemedicine Analitik')
        verbose_name_plural = _('Telemedicine Analitikleri')
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user} - {self.date}"
