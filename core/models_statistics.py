from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json

class SystemStatistics(models.Model):
    """
    Sistem istatistikleri modeli. Belirli bir zaman dilimindeki sisteme ait istatistikleri tutar.
    """
    date = models.DateField(
        unique=True,
        verbose_name=_('Tarih')
    )
    total_patients = models.IntegerField(
        default=0,
        verbose_name=_('Toplam Hasta Sayısı')
    )
    total_doctors = models.IntegerField(
        default=0,
        verbose_name=_('Toplam Doktor Sayısı')
    )
    total_appointments = models.IntegerField(
        default=0,
        verbose_name=_('Toplam Randevu Sayısı')
    )
    completed_appointments = models.IntegerField(
        default=0,
        verbose_name=_('Tamamlanan Randevu Sayısı')
    )
    cancelled_appointments = models.IntegerField(
        default=0,
        verbose_name=_('İptal Edilen Randevu Sayısı')
    )
    total_treatments = models.IntegerField(
        default=0,
        verbose_name=_('Toplam Tedavi Sayısı')
    )
    daily_active_users = models.IntegerField(
        default=0,
        verbose_name=_('Günlük Aktif Kullanıcı Sayısı')
    )
    data_json = models.JSONField(
        default=dict,
        verbose_name=_('Ek Veriler (JSON)'),
        help_text=_('Bu alana ekstra istatistik verilerini JSON formatında kaydedebilirsiniz.')
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
        verbose_name = _('Sistem İstatistiği')
        verbose_name_plural = _('Sistem İstatistikleri')
        ordering = ['-date']
    
    def __str__(self):
        return f"İstatistik: {self.date}"
    
    def get_data_as_dict(self):
        if isinstance(self.data_json, str):
            return json.loads(self.data_json)
        return self.data_json

class DoctorStatistics(models.Model):
    """
    Doktor istatistikleri modeli. Belirli bir zaman dilimindeki doktorlara ait istatistikleri tutar.
    """
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='statistics',
        verbose_name=_('Doktor'),
        limit_choices_to={'user_type': 'doctor'}
    )
    date = models.DateField(
        verbose_name=_('Tarih')
    )
    appointment_count = models.IntegerField(
        default=0,
        verbose_name=_('Randevu Sayısı')
    )
    completed_appointment_count = models.IntegerField(
        default=0,
        verbose_name=_('Tamamlanan Randevu Sayısı')
    )
    treatment_count = models.IntegerField(
        default=0,
        verbose_name=_('Tedavi Sayısı')
    )
    prescription_count = models.IntegerField(
        default=0,
        verbose_name=_('Reçete Sayısı')
    )
    lab_test_count = models.IntegerField(
        default=0,
        verbose_name=_('Laboratuvar Testi Sayısı')
    )
    average_appointment_duration = models.FloatField(
        default=0.0,
        verbose_name=_('Ortalama Randevu Süresi (dakika)')
    )
    data_json = models.JSONField(
        default=dict,
        verbose_name=_('Ek Veriler (JSON)')
    )
    
    class Meta:
        verbose_name = _('Doktor İstatistiği')
        verbose_name_plural = _('Doktor İstatistikleri')
        ordering = ['-date']
        unique_together = ['doctor', 'date']
    
    def __str__(self):
        return f"{self.doctor} - {self.date}"

class ReportTemplate(models.Model):
    """
    Rapor şablonu modeli. Özel raporlar oluşturmak için kullanılır.
    """
    REPORT_TYPE_CHOICES = [
        ('doctor_performance', _('Doktor Performans Raporu')),
        ('patient_statistics', _('Hasta İstatistikleri Raporu')),
        ('financial', _('Finansal Rapor')),
        ('appointment', _('Randevu Raporu')),
        ('treatment', _('Tedavi Raporu')),
        ('custom', _('Özel Rapor')),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Şablon Adı')
    )
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES,
        verbose_name=_('Rapor Tipi')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Açıklama')
    )
    query = models.TextField(
        verbose_name=_('SQL Sorgusu'),
        help_text=_('Bu şablonu kullanarak rapor oluşturulduğunda çalıştırılacak SQL sorgusu.')
    )
    columns = models.JSONField(
        default=list,
        verbose_name=_('Sütunlar'),
        help_text=_('Raporda gösterilecek sütunlar. JSON formatında: [{"name": "sütun_adı", "display": "Gösterim Adı"}]')
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
        verbose_name = _('Rapor Şablonu')
        verbose_name_plural = _('Rapor Şablonları')
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

class GeneratedReport(models.Model):
    """
    Oluşturulan rapor modeli. ReportTemplate kullanılarak oluşturulan raporları temsil eder.
    """
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name=_('Rapor Şablonu')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Rapor Adı')
    )
    parameters = models.JSONField(
        default=dict,
        verbose_name=_('Parametreler'),
        help_text=_('Rapor oluşturulurken kullanılan parametreler. JSON formatında.')
    )
    result_data = models.JSONField(
        default=list,
        verbose_name=_('Sonuç Verileri'),
        help_text=_('Rapor sonucu. JSON formatında.')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports',
        verbose_name=_('Oluşturan')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    report_file = models.FileField(
        upload_to='reports/',
        blank=True,
        null=True,
        verbose_name=_('Rapor Dosyası')
    )
    
    class Meta:
        verbose_name = _('Oluşturulan Rapor')
        verbose_name_plural = _('Oluşturulan Raporlar')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%Y-%m-%d')})"
