from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# İletişim modelleri için admin kayıtları
try:
    from .models_communication import Notification, Message, EmailTemplate
    
    @admin.register(Notification)
    class NotificationAdmin(admin.ModelAdmin):
        list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
        list_filter = ('notification_type', 'is_read', 'created_at')
        search_fields = ('user__username', 'title', 'message')
        date_hierarchy = 'created_at'
        
    @admin.register(Message)
    class MessageAdmin(admin.ModelAdmin):
        list_display = ('sender', 'receiver', 'subject', 'is_read', 'created_at')
        list_filter = ('is_read', 'created_at')
        search_fields = ('sender__username', 'receiver__username', 'subject', 'content')
        date_hierarchy = 'created_at'
    
    @admin.register(EmailTemplate)
    class EmailTemplateAdmin(admin.ModelAdmin):
        list_display = ('name', 'template_type', 'subject', 'is_active')
        list_filter = ('template_type', 'is_active')
        search_fields = ('name', 'subject', 'content')
except ImportError:
    pass

# İstatistik ve raporlama modelleri için admin kayıtları
try:
    from .models_statistics import SystemStatistics, DoctorStatistics, ReportTemplate, GeneratedReport
    
    @admin.register(SystemStatistics)
    class SystemStatisticsAdmin(admin.ModelAdmin):
        list_display = ('date', 'total_patients', 'total_doctors', 'total_appointments', 'completed_appointments')
        list_filter = ('date',)
        date_hierarchy = 'date'
        
    @admin.register(DoctorStatistics)
    class DoctorStatisticsAdmin(admin.ModelAdmin):
        list_display = ('doctor', 'date', 'appointment_count', 'completed_appointment_count', 'treatment_count')
        list_filter = ('date', 'doctor')
        date_hierarchy = 'date'
        search_fields = ('doctor__username', 'doctor__first_name', 'doctor__last_name')
        
    @admin.register(ReportTemplate)
    class ReportTemplateAdmin(admin.ModelAdmin):
        list_display = ('name', 'report_type', 'is_active')
        list_filter = ('report_type', 'is_active')
        search_fields = ('name', 'description')
        
    @admin.register(GeneratedReport)
    class GeneratedReportAdmin(admin.ModelAdmin):
        list_display = ('name', 'template', 'created_by', 'created_at')
        list_filter = ('template', 'created_at')
        search_fields = ('name', 'created_by__username')
        date_hierarchy = 'created_at'
except ImportError:
    pass
