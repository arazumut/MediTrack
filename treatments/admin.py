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

# Yeni modeller için admin kayıtları
try:
    from .models_medical_history import MedicalHistory

    @admin.register(MedicalHistory)
    class MedicalHistoryAdmin(admin.ModelAdmin):
        list_display = ('patient', 'condition_type', 'condition_name', 'diagnosed_date', 'is_active')
        list_filter = ('condition_type', 'is_active', 'diagnosed_date')
        search_fields = ('condition_name', 'notes', 'patient__username', 'patient__first_name', 'patient__last_name')
        date_hierarchy = 'diagnosed_date'
except ImportError:
    pass

try:
    from .models_lab import LabTest, TestResult

    class TestResultInline(admin.StackedInline):
        model = TestResult
        can_delete = False
        
    @admin.register(LabTest)
    class LabTestAdmin(admin.ModelAdmin):
        list_display = ('test_name', 'patient', 'doctor', 'status', 'requested_date', 'completed_date')
        list_filter = ('status', 'requested_date', 'doctor')
        search_fields = ('test_name', 'test_details', 'patient__username', 'patient__first_name', 'patient__last_name')
        inlines = [TestResultInline]
        date_hierarchy = 'requested_date'
        
    @admin.register(TestResult)
    class TestResultAdmin(admin.ModelAdmin):
        list_display = ('get_test_name', 'get_patient', 'is_normal', 'created_at')
        list_filter = ('is_normal', 'created_at')
        search_fields = ('result_text', 'notes', 'lab_test__test_name', 'lab_test__patient__username')
        
        def get_test_name(self, obj):
            return obj.lab_test.test_name
        get_test_name.short_description = _('Test Adı')
        
        def get_patient(self, obj):
            return obj.lab_test.patient
        get_patient.short_description = _('Hasta')
except ImportError:
    pass

try:
    from .models_medications import Medication, MedicationInteraction
    
    @admin.register(Medication)
    class MedicationAdmin(admin.ModelAdmin):
        list_display = ('name', 'active_ingredient', 'is_prescription', 'drug_code')
        list_filter = ('is_prescription', 'created_at')
        search_fields = ('name', 'active_ingredient', 'description', 'drug_code')
        
    @admin.register(MedicationInteraction)
    class MedicationInteractionAdmin(admin.ModelAdmin):
        list_display = ('medication1', 'medication2', 'severity')
        list_filter = ('severity',)
        search_fields = ('medication1__name', 'medication2__name', 'description', 'recommendations')
except ImportError:
    pass

try:
    from .models_imaging import MedicalImage, Report
    
    @admin.register(MedicalImage)
    class MedicalImageAdmin(admin.ModelAdmin):
        list_display = ('patient', 'image_type', 'body_part', 'doctor', 'taken_date')
        list_filter = ('image_type', 'taken_date', 'doctor')
        search_fields = ('body_part', 'description', 'patient__username', 'patient__first_name', 'patient__last_name')
        date_hierarchy = 'taken_date'
        
    @admin.register(Report)
    class ReportAdmin(admin.ModelAdmin):
        list_display = ('patient', 'report_type', 'title', 'doctor', 'valid_from', 'valid_until')
        list_filter = ('report_type', 'valid_from', 'doctor')
        search_fields = ('title', 'content', 'patient__username', 'patient__first_name', 'patient__last_name')
        date_hierarchy = 'valid_from'
except ImportError:
    pass
