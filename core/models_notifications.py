"""
Advanced Notification System for MediTracked
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class NotificationType(models.TextChoices):
    """Bildirim türleri"""
    APPOINTMENT_REMINDER = 'appointment_reminder', _('Randevu Hatırlatması')
    APPOINTMENT_CANCELLED = 'appointment_cancelled', _('Randevu İptali')
    APPOINTMENT_CONFIRMED = 'appointment_confirmed', _('Randevu Onayı')
    LAB_RESULT_READY = 'lab_result_ready', _('Lab Sonucu Hazır')
    PRESCRIPTION_READY = 'prescription_ready', _('Reçete Hazır')
    TREATMENT_COMPLETED = 'treatment_completed', _('Tedavi Tamamlandı')
    MEDICATION_REMINDER = 'medication_reminder', _('İlaç Hatırlatması')
    SYSTEM_MAINTENANCE = 'system_maintenance', _('Sistem Bakımı')
    DOCTOR_SCHEDULE_CHANGE = 'doctor_schedule_change', _('Doktor Program Değişikliği')
    EMERGENCY_ALERT = 'emergency_alert', _('Acil Durum Uyarısı')


class NotificationPriority(models.TextChoices):
    """Bildirim öncelik seviyeleri"""
    LOW = 'low', _('Düşük')
    NORMAL = 'normal', _('Normal')
    HIGH = 'high', _('Yüksek')
    URGENT = 'urgent', _('Acil')


class Notification(models.Model):
    """
    Gelişmiş bildirim modeli
    """
    # Alıcı - Use null=True for migration purposes
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Alıcı'),
        null=True
    )
    
    # Gönderen (opsiyonel, sistem bildirimleri için None olabilir)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True,
        verbose_name=_('Gönderen')
    )
    
    # Bildirim detayları
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        verbose_name=_('Bildirim Türü')
    )
    
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        verbose_name=_('Öncelik')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Başlık')
    )
    
    message = models.TextField(
        verbose_name=_('Mesaj')
    )
    
    # İlişkili nesne (Generic Foreign Key ile herhangi bir modele bağlanabilir)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Durum
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Okundu mu?')
    )
    
    is_sent_via_email = models.BooleanField(
        default=False,
        verbose_name=_('E-posta ile gönderildi mi?')
    )
    
    is_sent_via_sms = models.BooleanField(
        default=False,
        verbose_name=_('SMS ile gönderildi mi?')
    )
    
    # Zamanlama
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Okunma Tarihi')
    )
    
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Zamanlanmış Gönderim')
    )
    
    # Ek veriler (JSON formatında)
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Ek Veriler')
    )
    
    class Meta:
        verbose_name = _('Bildirim')
        verbose_name_plural = _('Bildirimler')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['scheduled_for']),
        ]
    
    def __str__(self):
        return f"{self.recipient} - {self.title}"
    
    def mark_as_read(self):
        """Bildirimi okundu olarak işaretle"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def get_priority_color(self):
        """Öncelik seviyesine göre renk döndür"""
        colors = {
            'low': 'secondary',
            'normal': 'primary', 
            'high': 'warning',
            'urgent': 'danger'
        }
        return colors.get(self.priority, 'primary')
    
    def get_icon(self):
        """Bildirim türüne göre ikon döndür"""
        icons = {
            'appointment_reminder': 'calendar-alt',
            'appointment_cancelled': 'calendar-times',
            'appointment_confirmed': 'calendar-check',
            'lab_result_ready': 'flask',
            'prescription_ready': 'pills',
            'treatment_completed': 'check-circle',
            'medication_reminder': 'clock',
            'system_maintenance': 'tools',
            'doctor_schedule_change': 'user-md',
            'emergency_alert': 'exclamation-triangle'
        }
        return icons.get(self.notification_type, 'bell')


class NotificationPreference(models.Model):
    """
    Kullanıcı bildirim tercihleri
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('Kullanıcı')
    )
    
    # E-posta bildirimleri
    email_appointment_reminders = models.BooleanField(
        default=True,
        verbose_name=_('Randevu hatırlatmaları (E-posta)')
    )
    
    email_lab_results = models.BooleanField(
        default=True,
        verbose_name=_('Lab sonuçları (E-posta)')
    )
    
    email_prescription_ready = models.BooleanField(
        default=True,
        verbose_name=_('Reçete hazır (E-posta)')
    )
    
    email_system_updates = models.BooleanField(
        default=False,
        verbose_name=_('Sistem güncellemeleri (E-posta)')
    )
    
    # SMS bildirimleri
    sms_appointment_reminders = models.BooleanField(
        default=False,
        verbose_name=_('Randevu hatırlatmaları (SMS)')
    )
    
    sms_emergency_alerts = models.BooleanField(
        default=True,
        verbose_name=_('Acil durum uyarıları (SMS)')
    )
    
    # Push bildirimleri
    push_notifications = models.BooleanField(
        default=True,
        verbose_name=_('Push bildirimleri')
    )
    
    # Hatırlatma zamanları
    appointment_reminder_hours = models.PositiveIntegerField(
        default=24,
        verbose_name=_('Randevu hatırlatma saati (saat önce)')
    )
    
    medication_reminder_enabled = models.BooleanField(
        default=False,
        verbose_name=_('İlaç hatırlatmaları aktif')
    )
    
    medication_reminder_times = models.JSONField(
        default=list,
        verbose_name=_('İlaç hatırlatma saatleri'),
        help_text=_('["08:00", "12:00", "18:00"] formatında')
    )
    
    class Meta:
        verbose_name = _('Bildirim Tercihi')
        verbose_name_plural = _('Bildirim Tercihleri')
    
    def __str__(self):
        return f"{self.user} - Bildirim Tercihleri"


class NotificationTemplate(models.Model):
    """
    Bildirim şablonları
    """
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        unique=True,
        verbose_name=_('Bildirim Türü')
    )
    
    title_template = models.CharField(
        max_length=200,
        verbose_name=_('Başlık Şablonu'),
        help_text=_('Django template syntax kullanabilirsiniz: {{ variable }}')
    )
    
    message_template = models.TextField(
        verbose_name=_('Mesaj Şablonu'),
        help_text=_('Django template syntax kullanabilirsiniz')
    )
    
    email_template = models.TextField(
        blank=True,
        verbose_name=_('E-posta Şablonu (HTML)'),
        help_text=_('E-posta için özel HTML şablon')
    )
    
    sms_template = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_('SMS Şablonu'),
        help_text=_('SMS için kısa metin (160 karakter max)')
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
        verbose_name = _('Bildirim Şablonu')
        verbose_name_plural = _('Bildirim Şablonları')
    
    def __str__(self):
        return f"{self.get_notification_type_display()} Şablonu"


class NotificationLog(models.Model):
    """
    Gönderilen bildirimlerin logları
    """
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_('Bildirim')
    )
    
    delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('web', _('Web')),
            ('email', _('E-posta')),
            ('sms', _('SMS')),
            ('push', _('Push'))
        ],
        verbose_name=_('Gönderim Yöntemi')
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Beklemede')),
            ('sent', _('Gönderildi')),
            ('delivered', _('Teslim Edildi')),
            ('failed', _('Başarısız')),
            ('bounced', _('Geri Döndü'))
        ],
        default='pending',
        verbose_name=_('Durum')
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name=_('Hata Mesajı')
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Gönderilme Tarihi')
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Teslim Edilme Tarihi')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        verbose_name = _('Bildirim Logu')
        verbose_name_plural = _('Bildirim Logları')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification.title} - {self.get_delivery_method_display()} - {self.get_status_display()}"
