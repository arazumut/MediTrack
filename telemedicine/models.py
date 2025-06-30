"""
Telemedicine Models for MediTracked
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.validators import URLValidator
from appointments.models import Appointment
import uuid


class TelemedicineAppointment(models.Model):
    """
    Tele-tıp randevu modeli
    """
    STATUS_CHOICES = [
        ('scheduled', _('Zamanlandı')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
        ('no_show', _('Katılım Sağlanmadı')),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telemedicine_patient_appointments',
        verbose_name=_('Hasta'),
        limit_choices_to={'user_type': 'patient'}
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telemedicine_doctor_appointments',
        verbose_name=_('Doktor'),
        limit_choices_to={'user_type': 'doctor'}
    )
    
    date = models.DateField(
        verbose_name=_('Tarih')
    )
    
    time = models.TimeField(
        verbose_name=_('Saat')
    )
    
    duration = models.PositiveIntegerField(
        default=30,
        verbose_name=_('Süre (dakika)')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name=_('Durum')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Açıklama')
    )
    
    chief_complaint = models.TextField(
        blank=True,
        verbose_name=_('Ana Şikayet')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_telemedicine_appointments',
        verbose_name=_('Oluşturan')
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
        verbose_name = _('Tele-tıp Randevusu')
        verbose_name_plural = _('Tele-tıp Randevuları')
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.patient} - Dr. {self.doctor} - {self.date} {self.time}"
    
    def is_past(self):
        """Randevu geçmiş mi?"""
        now = timezone.now()
        appointment_datetime = timezone.make_aware(timezone.datetime.combine(self.date, self.time))
        return appointment_datetime < now


class VideoSession(models.Model):
    """
    Video görüşme oturumu modeli
    """
    appointment = models.ForeignKey(
        TelemedicineAppointment,
        on_delete=models.CASCADE,
        related_name='video_sessions',
        verbose_name=_('Randevu')
    )
    
    room_name = models.CharField(
        max_length=255,
        verbose_name=_('Oda Adı')
    )
    
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='started_sessions',
        verbose_name=_('Başlatan')
    )
    
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Başlangıç Zamanı')
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Bitiş Zamanı')
    )
    
    ended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ended_sessions',
        verbose_name=_('Sonlandıran')
    )
    
    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Süre (saniye)')
    )
    
    recording_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Kayıt URL')
    )
    
    connection_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', _('Mükemmel')),
            ('good', _('İyi')),
            ('fair', _('Orta')),
            ('poor', _('Kötü')),
        ],
        blank=True,
        null=True,
        verbose_name=_('Bağlantı Kalitesi')
    )
    
    class Meta:
        verbose_name = _('Video Oturumu')
        verbose_name_plural = _('Video Oturumları')
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Oturum: {self.appointment} - {self.start_time}"
    
    def get_duration(self):
        """Oturum süresini hesapla"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def save(self, *args, **kwargs):
        if self.end_time and not self.duration_seconds:
            self.duration_seconds = self.get_duration()
        super().save(*args, **kwargs)


class TelemedDocument(models.Model):
    """
    Tele-tıp belge modeli
    """
    appointment = models.ForeignKey(
        TelemedicineAppointment,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Randevu')
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Başlık')
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('lab_result', _('Laboratuvar Sonucu')),
            ('prescription', _('Reçete')),
            ('medical_image', _('Tıbbi Görüntü')),
            ('referral', _('Sevk')),
            ('other', _('Diğer')),
        ],
        verbose_name=_('Belge Türü')
    )
    
    file = models.FileField(
        upload_to='telemedicine/documents/',
        verbose_name=_('Dosya')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Açıklama')
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_telemedicine_documents',
        verbose_name=_('Yükleyen')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        verbose_name = _('Tele-tıp Belgesi')
        verbose_name_plural = _('Tele-tıp Belgeleri')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.appointment}"


class TelemedPrescription(models.Model):
    """
    Tele-tıp reçete modeli
    """
    appointment = models.ForeignKey(
        TelemedicineAppointment,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name=_('Randevu')
    )
    
    medications = models.JSONField(
        verbose_name=_('İlaçlar'),
        help_text=_('İlaç listesi ve dozaj bilgileri')
    )
    
    instructions = models.TextField(
        verbose_name=_('Talimatlar')
    )
    
    duration_days = models.PositiveIntegerField(
        verbose_name=_('Süre (gün)')
    )
    
    is_renewable = models.BooleanField(
        default=False,
        verbose_name=_('Yenilenebilir mi?')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_telemedicine_prescriptions',
        verbose_name=_('Oluşturan Doktor'),
        limit_choices_to={'user_type': 'doctor'}
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        verbose_name = _('Tele-tıp Reçetesi')
        verbose_name_plural = _('Tele-tıp Reçeteleri')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reçete: {self.appointment}"


class TelemedNote(models.Model):
    """
    Tele-tıp not modeli
    """
    appointment = models.ForeignKey(
        TelemedicineAppointment,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Randevu')
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name=_('Başlık')
    )
    
    content = models.TextField(
        verbose_name=_('İçerik')
    )
    
    note_type = models.CharField(
        max_length=50,
        choices=[
            ('diagnosis', _('Teşhis')),
            ('treatment_plan', _('Tedavi Planı')),
            ('follow_up', _('Takip')),
            ('general', _('Genel Not')),
        ],
        default='general',
        verbose_name=_('Not Türü')
    )
    
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('Özel Not mu?'),
        help_text=_('Özel notlar sadece doktor tarafından görülebilir')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_telemedicine_notes',
        verbose_name=_('Oluşturan')
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
        verbose_name = _('Tele-tıp Notu')
        verbose_name_plural = _('Tele-tıp Notları')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.appointment}"


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
                duration = self.end_time - self.actual_start_time
                self.duration_minutes = int(duration.total_seconds() / 60)
                
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
        verbose_name=_('Zaman')
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
        default=True,
        verbose_name=_('Otomatik Sonlandır')
    )
    
    class Meta:
        verbose_name = _('Telemedicine Ayarları')
        verbose_name_plural = _('Telemedicine Ayarları')
    
    def __str__(self):
        return f"{self.user} Ayarları"
