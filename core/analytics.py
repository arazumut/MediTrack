"""
Advanced Analytics and Dashboard Data Provider for MediTracked
"""
from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

from appointments.models import Appointment
from treatments.models import Treatment, Prescription
from treatments.models_lab import LabTest
from treatments.models_medical_history import MedicalHistory
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardAnalytics:
    """
    Dashboard için gelişmiş analitik veriler sağlar
    """
    
    def __init__(self, user=None, date_range_days=30):
        self.user = user
        self.date_range_days = date_range_days
        self.start_date = timezone.now().date() - timedelta(days=date_range_days)
        self.end_date = timezone.now().date()
    
    def get_appointment_stats(self):
        """Randevu istatistikleri"""
        queryset = Appointment.objects.filter(
            date__range=[self.start_date, self.end_date]
        )
        
        if self.user:
            if self.user.is_doctor():
                queryset = queryset.filter(doctor=self.user)
            elif self.user.is_patient():
                queryset = queryset.filter(patient=self.user)
        
        total_appointments = queryset.count()
        completed = queryset.filter(status='completed').count()
        cancelled = queryset.filter(status='cancelled').count()
        planned = queryset.filter(status='planned').count()
        
        # Günlük randevu dağılımı
        daily_appointments = defaultdict(int)
        for appointment in queryset:
            day_key = appointment.date.strftime('%Y-%m-%d')
            daily_appointments[day_key] += 1
        # Günlük randevu sayısını sıralı hale getir
        daily_appointments= sorted(daily_appointments.items())
        
        return {
            'total': total_appointments,
            'completed': completed,
            'cancelled': cancelled,
            'planned': planned,
            'completion_rate': (completed / total_appointments * 100) if total_appointments > 0 else 0,
            'daily_distribution': dict(daily_appointments)
        }
    
    def get_patient_stats(self):
        """Hasta istatistikleri"""
        if not self.user or not (self.user.is_doctor() or self.user.is_admin_user()):
            return {}
        
        patients = User.objects.filter(user_type='patient')
        
        # Son randevu tarihleri
        recent_patients = patients.filter(
            patient_appointments__date__gte=self.start_date
        ).distinct().count()
        
        # Aktif kronik hastalık sayısı
        chronic_conditions = MedicalHistory.objects.filter(
            condition_type='chronic',
            is_active=True
        ).count()
        
        # Yeni hasta kayıtları
        new_patients = patients.filter(
            date_joined__date__range=[self.start_date, self.end_date]
        ).count()
        
        return {
            'total_patients': patients.count(),
            'recent_patients': recent_patients,
            'chronic_conditions': chronic_conditions,
            'new_patients': new_patients
        }
    
    def get_treatment_stats(self):
        """Tedavi istatistikleri"""
        queryset = Treatment.objects.filter(
            created_at__date__range=[self.start_date, self.end_date]
        )
        
        if self.user and self.user.is_doctor():
            queryset = queryset.filter(appointment__doctor=self.user)
        
        total_treatments = queryset.count()
        
        # En sık verilen teşhisler
        common_diagnoses = queryset.values('diagnosis').annotate(
            count=Count('diagnosis')
        ).order_by('-count')[:10]
        
        # Reçete istatistikleri
        prescriptions_count = Prescription.objects.filter(
            treatment__in=queryset
        ).count()
        
        avg_prescriptions_per_treatment = (
            prescriptions_count / total_treatments
        ) if total_treatments > 0 else 0
        
        return {
            'total_treatments': total_treatments,
            'prescriptions_count': prescriptions_count,
            'avg_prescriptions': round(avg_prescriptions_per_treatment, 2),
            'common_diagnoses': list(common_diagnoses)
        }
    
    def get_lab_test_stats(self):
        """Laboratuvar test istatistikleri"""
        queryset = LabTest.objects.filter(
            requested_date__date__range=[self.start_date, self.end_date]
        )
        
        if self.user and self.user.is_doctor():
            queryset = queryset.filter(doctor=self.user)
        
        total_tests = queryset.count()
        completed_tests = queryset.filter(status='completed').count()
        pending_tests = queryset.filter(status__in=['requested', 'in_progress']).count()
        
        # En sık istenen testler
        popular_tests = queryset.values('test_name').annotate(
            count=Count('test_name')
        ).order_by('-count')[:10]
        
        return {
            'total_tests': total_tests,
            'completed_tests': completed_tests,
            'pending_tests': pending_tests,
            'completion_rate': (completed_tests / total_tests * 100) if total_tests > 0 else 0,
            'popular_tests': list(popular_tests)
        }
    
    def get_doctor_performance(self):
        """Doktor performans metrikleri"""
        if not self.user or not self.user.is_doctor():
            return {}
        
        appointments = Appointment.objects.filter(
            doctor=self.user,
            date__range=[self.start_date, self.end_date]
        )
        
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        
        # Ortalama tedavi süresi (saniye)
        treatments = Treatment.objects.filter(
            appointment__doctor=self.user,
            created_at__date__range=[self.start_date, self.end_date]
        )
        
        # Hasta memnuniyet skoru (gelecekte eklenebilir)
        # satisfaction_score = self.calculate_satisfaction_score()
        
        return {
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'completion_rate': (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0,
            'total_treatments': treatments.count(),
            'avg_daily_patients': round(total_appointments / self.date_range_days, 1)
        }
    
    def get_monthly_trends(self):
        """Aylık trend verileri"""
        months_data = []
        
        for i in range(6):  # Son 6 ay
            month_start = (timezone.now().date().replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1]))
            
            appointments = Appointment.objects.filter(
                date__range=[month_start, month_end]
            )
            
            if self.user and self.user.is_doctor():
                appointments = appointments.filter(doctor=self.user)
            
            months_data.append({
                'month': month_start.strftime('%B %Y'),
                'appointments': appointments.count(),
                'treatments': Treatment.objects.filter(
                    appointment__in=appointments
                ).count()
            })
        
        return list(reversed(months_data))
    
    def get_comprehensive_dashboard_data(self):
        """Tüm dashboard verilerini toplar"""
        return {
            'appointment_stats': self.get_appointment_stats(),
            'patient_stats': self.get_patient_stats(),
            'treatment_stats': self.get_treatment_stats(),
            'lab_test_stats': self.get_lab_test_stats(),
            'doctor_performance': self.get_doctor_performance(),
            'monthly_trends': self.get_monthly_trends(),
            'date_range': {
                'start': self.start_date,
                'end': self.end_date,
                'days': self.date_range_days
            }
        }


class ReportGenerator:
    """
    Çeşitli raporlar oluşturur
    """
    
    @staticmethod
    def generate_doctor_summary_report(doctor, start_date, end_date):
        """Doktor özet raporu"""
        appointments = Appointment.objects.filter(
            doctor=doctor,
            date__range=[start_date, end_date]
        )
        
        treatments = Treatment.objects.filter(
            appointment__doctor=doctor,
            created_at__date__range=[start_date, end_date]
        )
        
        return {
            'doctor': doctor,
            'period': {'start': start_date, 'end': end_date},
            'total_appointments': appointments.count(),
            'completed_appointments': appointments.filter(status='completed').count(),
            'total_treatments': treatments.count(),
            'unique_patients': appointments.values('patient').distinct().count(),
            'lab_tests_ordered': LabTest.objects.filter(
                doctor=doctor,
                requested_date__date__range=[start_date, end_date]
            ).count(),
            'prescriptions_written': Prescription.objects.filter(
                treatment__appointment__doctor=doctor,
                created_at__date__range=[start_date, end_date]
            ).count()
        }
    
    @staticmethod
    def generate_patient_health_summary(patient):
        """Hasta sağlık özeti"""
        appointments = Appointment.objects.filter(patient=patient)
        treatments = Treatment.objects.filter(appointment__patient=patient)
        
        return {
            'patient': patient,
            'total_appointments': appointments.count(),
            'last_appointment': appointments.order_by('-date').first(),
            'chronic_conditions': MedicalHistory.objects.filter(
                patient=patient,
                condition_type='chronic',
                is_active=True
            ),
            'allergies': MedicalHistory.objects.filter(
                patient=patient,
                condition_type='allergy',
                is_active=True
            ),
            'current_medications': MedicalHistory.objects.filter(
                patient=patient,
                condition_type='medication',
                is_active=True
            ),
            'recent_treatments': treatments.order_by('-created_at')[:5],
            'pending_lab_tests': LabTest.objects.filter(
                patient=patient,
                status__in=['requested', 'in_progress']
            )
        }
