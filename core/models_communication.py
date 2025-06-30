from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class CommunicationNotification(models.Model):
    """
    Bildirim modeli. Sistem içinde kullanıcılara gönderilen bildirimleri temsil eder.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('appointment', _('Randevu Bildirimi')),
        ('test_result', _('Test Sonucu Bildirimi')),
        ('prescription', _('Reçete Bildirimi')),
        ('message', _('Mesaj Bildirimi')),
        ('system', _('Sistem Bildirimi')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='communication_notifications',
        verbose_name=_('Kullanıcı')
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name=_('Bildirim Tipi')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Başlık')
    )
    message = models.TextField(
        verbose_name=_('Mesaj')
    )
    related_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('İlgili URL')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Okundu mu?')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        verbose_name = _('İletişim Bildirimi')
        verbose_name_plural = _('İletişim Bildirimleri')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.title}"
    
    def mark_as_read(self):
        """
        Bildirimi okundu olarak işaretler
        """
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

class Message(models.Model):
    """
    Mesaj modeli. Kullanıcılar arasındaki mesajlaşmaları temsil eder.
    """
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('Gönderen')
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('Alıcı')
    )
    subject = models.CharField(
        max_length=200,
        verbose_name=_('Konu')
    )
    content = models.TextField(
        verbose_name=_('İçerik')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Okundu mu?')
    )
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('Üst Mesaj')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        verbose_name = _('Mesaj')
        verbose_name_plural = _('Mesajlar')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.subject}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])

class EmailTemplate(models.Model):
    """
    E-posta şablonu modeli. Sistem tarafından gönderilen e-postaların şablonlarını temsil eder.
    """
    TEMPLATE_TYPE_CHOICES = [
        ('appointment_reminder', _('Randevu Hatırlatma')),
        ('appointment_confirmation', _('Randevu Onayı')),
        ('appointment_cancellation', _('Randevu İptali')),
        ('test_result', _('Test Sonucu Bildirimi')),
        ('prescription', _('Reçete Bildirimi')),
        ('welcome', _('Hoş Geldiniz')),
        ('password_reset', _('Şifre Sıfırlama')),
        ('custom', _('Özel Şablon')),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Şablon Adı')
    )
    template_type = models.CharField(
        max_length=30,
        choices=TEMPLATE_TYPE_CHOICES,
        verbose_name=_('Şablon Tipi')
    )
    subject = models.CharField(
        max_length=200,
        verbose_name=_('E-posta Konusu')
    )
    content = models.TextField(
        verbose_name=_('E-posta İçeriği'),
        help_text=_('HTML kullanabilirsiniz. Değişkenler için {{değişken_adı}} formatını kullanın.')
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
        verbose_name = _('E-posta Şablonu')
        verbose_name_plural = _('E-posta Şablonları')
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
