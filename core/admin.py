from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from users.models import User
from .models_theme import UserThemePreference
from .models_statistics import DoctorPerformanceMetric
from .models_communication import CommunicationNotification, Message, EmailTemplate
from .models_notifications import Notification, NotificationType, NotificationTemplate, NotificationLog

@admin.register(CommunicationNotification)
class CommunicationNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
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
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'subject', 'content')
    date_hierarchy = 'created_at'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'priority', 'created_at')
    search_fields = ('recipient__username', 'recipient__email', 'title', 'message')
    date_hierarchy = 'created_at'

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'is_active')
    list_filter = ('notification_type', 'is_active')
    search_fields = ('title_template', 'message_template')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification', 'delivery_method', 'status', 'sent_at')
    list_filter = ('delivery_method', 'status', 'sent_at')
    search_fields = ('notification__title', 'error_message')
    date_hierarchy = 'sent_at'

@admin.register(DoctorPerformanceMetric)
class DoctorPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'appointments_count', 'treatments_count', 'average_rating')
    list_filter = ('date',)
    search_fields = ('doctor__username', 'doctor__first_name', 'doctor__last_name')
    date_hierarchy = 'date'

@admin.register(UserThemePreference)
class UserThemePreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'sidebar_mode', 'updated_at')
    list_filter = ('theme', 'sidebar_mode')
    search_fields = ('user__username', 'user__email')
