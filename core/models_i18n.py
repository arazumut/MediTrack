"""
Internationalization Management for MediTracked
Çoklu dil desteği yönetimi
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json


class Language(models.Model):
    """
    Desteklenen diller
    """
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('Dil Kodu'),
        help_text=_('ISO 639-1 dil kodu (örn: tr, en, de)')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Dil Adı')
    )
    
    native_name = models.CharField(
        max_length=100,
        verbose_name=_('Yerel Adı'),
        help_text=_('Dilin kendi dilindeki adı')
    )
    
    flag_emoji = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_('Bayrak Emoji')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif mi?')
    )
    
    is_rtl = models.BooleanField(
        default=False,
        verbose_name=_('Sağdan Sola mı?'),
        help_text=_('Arapça, İbranice gibi diller için')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Sıralama')
    )
    
    class Meta:
        verbose_name = _('Dil')
        verbose_name_plural = _('Diller')
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.flag_emoji} {self.native_name}"


class UserLanguagePreference(models.Model):
    """
    Kullanıcı dil tercihleri
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='language_preference',
        verbose_name=_('Kullanıcı')
    )
    
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        verbose_name=_('Tercih Edilen Dil')
    )
    
    date_format = models.CharField(
        max_length=20,
        choices=[
            ('DD/MM/YYYY', 'DD/MM/YYYY'),
            ('MM/DD/YYYY', 'MM/DD/YYYY'),
            ('YYYY-MM-DD', 'YYYY-MM-DD'),
            ('DD.MM.YYYY', 'DD.MM.YYYY'),
        ],
        default='DD/MM/YYYY',
        verbose_name=_('Tarih Formatı')
    )
    
    time_format = models.CharField(
        max_length=10,
        choices=[
            ('24h', '24 Saat (14:30)'),
            ('12h', '12 Saat (2:30 PM)'),
        ],
        default='24h',
        verbose_name=_('Saat Formatı')
    )
    
    timezone = models.CharField(
        max_length=50,
        default='Europe/Istanbul',
        verbose_name=_('Saat Dilimi')
    )
    
    number_format = models.CharField(
        max_length=20,
        choices=[
            ('1,234.56', '1,234.56 (Anglo-Saxon)'),
            ('1.234,56', '1.234,56 (Continental European)'),
            ('1 234,56', '1 234,56 (French)'),
        ],
        default='1,234.56',
        verbose_name=_('Sayı Formatı')
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
        verbose_name = _('Kullanıcı Dil Tercihi')
        verbose_name_plural = _('Kullanıcı Dil Tercihleri')
    
    def __str__(self):
        return f"{self.user} - {self.language}"


class TranslationContext(models.Model):
    """
    Çeviri bağlamları - medikal terimler için özel çeviriler
    """
    CONTEXT_TYPES = [
        ('medical', _('Medikal Terimler')),
        ('ui', _('Kullanıcı Arayüzü')),
        ('notification', _('Bildirimler')),
        ('report', _('Raporlar')),
        ('appointment', _('Randevu')),
        ('treatment', _('Tedavi')),
        ('medication', _('İlaç')),
        ('diagnosis', _('Teşhis')),
    ]
    
    context_type = models.CharField(
        max_length=20,
        choices=CONTEXT_TYPES,
        verbose_name=_('Bağlam Türü')
    )
    
    source_text = models.TextField(
        verbose_name=_('Kaynak Metin'),
        help_text=_('Çevrilecek orijinal metin')
    )
    
    context_key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Bağlam Anahtarı'),
        help_text=_('Benzersiz anahtar (örn: diagnosis.diabetes)')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Açıklama'),
        help_text=_('Çevirmenler için açıklama')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktif mi?')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        verbose_name = _('Çeviri Bağlamı')
        verbose_name_plural = _('Çeviri Bağlamları')
        ordering = ['context_type', 'context_key']
    
    def __str__(self):
        return f"{self.context_type} - {self.context_key}"


class Translation(models.Model):
    """
    Çeviriler
    """
    context = models.ForeignKey(
        TranslationContext,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_('Bağlam')
    )
    
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        verbose_name=_('Dil')
    )
    
    translated_text = models.TextField(
        verbose_name=_('Çevrilmiş Metin')
    )
    
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Onaylandı mı?')
    )
    
    translator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Çevirmen')
    )
    
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_translations',
        verbose_name=_('İnceleyici')
    )
    
    quality_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Kalite Puanı'),
        help_text=_('1-5 arası kalite puanı')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notlar'),
        help_text=_('Çeviri ile ilgili notlar')
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
        verbose_name = _('Çeviri')
        verbose_name_plural = _('Çeviriler')
        unique_together = ['context', 'language']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.context.context_key} - {self.language.code}"


class MedicalTerminology(models.Model):
    """
    Medikal terminoloji sözlüğü
    """
    CATEGORY_CHOICES = [
        ('anatomy', _('Anatomi')),
        ('disease', _('Hastalık')),
        ('symptom', _('Semptom')),
        ('medication', _('İlaç')),
        ('procedure', _('Prosedür')),
        ('test', _('Test/Tahlil')),
        ('specialty', _('Uzmanlık')),
    ]
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name=_('Kategori')
    )
    
    term_en = models.CharField(
        max_length=200,
        verbose_name=_('İngilizce Terim')
    )
    
    term_tr = models.CharField(
        max_length=200,
        verbose_name=_('Türkçe Terim')
    )
    
    definition_en = models.TextField(
        blank=True,
        verbose_name=_('İngilizce Tanım')
    )
    
    definition_tr = models.TextField(
        blank=True,
        verbose_name=_('Türkçe Tanım')
    )
    
    synonyms = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Eş Anlamlılar'),
        help_text=_('{"en": ["synonym1", "synonym2"], "tr": ["eşanlamlı1"]}')
    )
    
    icd_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('ICD Kodu'),
        help_text=_('Hastalıklar için ICD-10 kodu')
    )
    
    is_commonly_used = models.BooleanField(
        default=False,
        verbose_name=_('Sık Kullanılan mı?')
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Kullanım Sayısı')
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
        verbose_name = _('Medikal Terminoloji')
        verbose_name_plural = _('Medikal Terminolojiler')
        ordering = ['category', 'term_en']
        indexes = [
            models.Index(fields=['term_en']),
            models.Index(fields=['term_tr']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.term_en} / {self.term_tr}"
    
    def increment_usage(self):
        """Kullanım sayısını artır"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class LocalizationSetting(models.Model):
    """
    Lokalizasyon ayarları
    """
    language = models.OneToOneField(
        Language,
        on_delete=models.CASCADE,
        related_name='localization_settings',
        verbose_name=_('Dil')
    )
    
    # Medikal birimler
    temperature_unit = models.CharField(
        max_length=10,
        choices=[
            ('celsius', '°C (Celsius)'),
            ('fahrenheit', '°F (Fahrenheit)'),
        ],
        default='celsius',
        verbose_name=_('Sıcaklık Birimi')
    )
    
    weight_unit = models.CharField(
        max_length=10,
        choices=[
            ('kg', 'Kilogram (kg)'),
            ('lb', 'Pound (lb)'),
        ],
        default='kg',
        verbose_name=_('Ağırlık Birimi')
    )
    
    height_unit = models.CharField(
        max_length=10,
        choices=[
            ('cm', 'Santimetre (cm)'),
            ('ft_in', 'Feet & Inches'),
        ],
        default='cm',
        verbose_name=_('Boy Birimi')
    )
    
    blood_pressure_unit = models.CharField(
        max_length=10,
        choices=[
            ('mmhg', 'mmHg'),
            ('kpa', 'kPa'),
        ],
        default='mmhg',
        verbose_name=_('Tansiyon Birimi')
    )
    
    # Adres formatı
    address_format = models.TextField(
        default='',
        verbose_name=_('Adres Formatı'),
        help_text=_('Adres gösterim formatı şablonu')
    )
    
    # Para birimi
    currency_code = models.CharField(
        max_length=3,
        default='TRY',
        verbose_name=_('Para Birimi Kodu')
    )
    
    currency_symbol = models.CharField(
        max_length=5,
        default='₺',
        verbose_name=_('Para Birimi Sembolü')
    )
    
    # Tarih ve saat formatları
    date_format_short = models.CharField(
        max_length=20,
        default='dd/mm/yyyy',
        verbose_name=_('Kısa Tarih Formatı')
    )
    
    date_format_long = models.CharField(
        max_length=50,
        default='dd mmmm yyyy',
        verbose_name=_('Uzun Tarih Formatı')
    )
    
    time_format = models.CharField(
        max_length=20,
        default='HH:mm',
        verbose_name=_('Saat Formatı')
    )
    
    first_day_of_week = models.IntegerField(
        choices=[
            (0, _('Pazar')),
            (1, _('Pazartesi')),
        ],
        default=1,
        verbose_name=_('Haftanın İlk Günü')
    )
    
    class Meta:
        verbose_name = _('Lokalizasyon Ayarı')
        verbose_name_plural = _('Lokalizasyon Ayarları')
    
    def __str__(self):
        return f"{self.language} - Lokalizasyon Ayarları"
