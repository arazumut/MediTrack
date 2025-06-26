from django.contrib import admin
from .models import TeleMedicineConsultation, TeleMedicineMessage, TeleMedicineSettings


@admin.register(TeleMedicineConsultation)
class TeleMedicineConsultationAdmin(admin.ModelAdmin):
    list_display = ['meeting_id', 'appointment', 'status', 'scheduled_start_time', 'actual_start_time', 'end_time']
    list_filter = ['status', 'consultation_type', 'scheduled_start_time']
    search_fields = ['meeting_id', 'appointment__patient__username', 'appointment__doctor__username']
    readonly_fields = ['meeting_id', 'actual_start_time', 'end_time']


@admin.register(TeleMedicineMessage)
class TeleMedicineMessageAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'sender', 'message_type', 'timestamp', 'is_read']
    list_filter = ['message_type', 'is_read', 'timestamp']
    search_fields = ['consultation__meeting_id', 'sender__username', 'content']


@admin.register(TeleMedicineSettings)
class TeleMedicineSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'default_camera_enabled', 'default_microphone_enabled', 'video_quality']
    list_filter = ['default_camera_enabled', 'default_microphone_enabled', 'video_quality']
    search_fields = ['user__username']
