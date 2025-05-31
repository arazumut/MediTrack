from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Treatment, Prescription

class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 1

@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('get_patient', 'get_doctor', 'get_date', 'diagnosis')
    list_filter = ('appointment__doctor', 'appointment__date')
    search_fields = ('diagnosis', 'notes', 'appointment__patient__username', 
                    'appointment__patient__first_name', 'appointment__patient__last_name')
    inlines = [PrescriptionInline]
    
    def get_patient(self, obj):
        return obj.appointment.patient
    get_patient.short_description = _('Hasta')
    get_patient.admin_order_field = 'appointment__patient__username'
    
    def get_doctor(self, obj):
        return obj.appointment.doctor
    get_doctor.short_description = _('Doktor')
    get_doctor.admin_order_field = 'appointment__doctor__username'
    
    def get_date(self, obj):
        return obj.appointment.date
    get_date.short_description = _('Tarih')
    get_date.admin_order_field = 'appointment__date'

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'dosage', 'get_patient', 'get_doctor')
    list_filter = ('treatment__appointment__doctor', 'treatment__appointment__date')
    search_fields = ('name', 'dosage', 'instructions')
    
    def get_patient(self, obj):
        return obj.treatment.appointment.patient
    get_patient.short_description = _('Hasta')
    
    def get_doctor(self, obj):
        return obj.treatment.appointment.doctor
    get_doctor.short_description = _('Doktor')
