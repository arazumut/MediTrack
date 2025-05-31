from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('patient__username', 'patient__first_name', 'patient__last_name', 
                    'doctor__username', 'doctor__first_name', 'doctor__last_name')
    date_hierarchy = 'date'
    fieldsets = (
        (None, {
            'fields': ('patient', 'doctor')
        }),
        (_('Randevu Bilgileri'), {
            'fields': ('date', 'time', 'description', 'status')
        }),
    )
