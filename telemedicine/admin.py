from django.contrib import admin
from .models import TeleconsultationSession, TeleconsultationMessage, TeleconsultationSettings


@admin.register(TeleconsultationSession)
class TeleconsultationSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'patient', 'doctor', 'status', 'scheduled_time', 'start_time', 'end_time']
    list_filter = ['status', 'session_type', 'scheduled_time']
    search_fields = ['session_id', 'patient__username', 'doctor__username']
    readonly_fields = ['session_id', 'start_time', 'end_time']
    
    fieldsets = (
        ('Session Details', {
            'fields': ('session_id', 'patient', 'doctor', 'status', 'session_type')
        }),
        ('Scheduling', {
            'fields': ('scheduled_time', 'duration_minutes', 'time_zone')
        }),
        ('Session Data', {
            'fields': ('start_time', 'end_time', 'room_url', 'recording_url')
        }),
        ('Additional Info', {
            'fields': ('notes', 'diagnosis', 'prescription', 'follow_up_required')
        }),
    )


@admin.register(TeleconsultationMessage)
class TeleconsultationMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'sender', 'message_type', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['session__session_id', 'sender__username', 'content']
    readonly_fields = ['timestamp']


@admin.register(TeleconsultationSettings)
class TeleconsultationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'enable_video', 'enable_audio', 'enable_screen_share']
    list_filter = ['enable_video', 'enable_audio', 'enable_screen_share']
    search_fields = ['user__username']
