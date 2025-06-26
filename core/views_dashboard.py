"""
Enhanced Dashboard Views with Analytics and Charts
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from .analytics import DashboardAnalytics, ReportGenerator
from appointments.models import Appointment
from treatments.models import Treatment
from treatments.models_lab import LabTest
from treatments.models_medical_history import MedicalHistory

User = get_user_model()


class EnhancedDashboardView(LoginRequiredMixin, TemplateView):
    """
    Gelişmiş dashboard görünümü
    """
    template_name = 'dashboards/enhanced_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Analitik verilerini al
        analytics = DashboardAnalytics(user=self.request.user)
        dashboard_data = analytics.get_comprehensive_dashboard_data()
        
        context.update(dashboard_data)
        context['user'] = self.request.user
        context['current_date'] = timezone.now().date()
        
        # Hızlı erişim linkleri
        context['quick_actions'] = self.get_quick_actions()
        
        # Son aktiviteler
        context['recent_activities'] = self.get_recent_activities()
        
        return context
    
    def get_quick_actions(self):
        """Kullanıcı tipine göre hızlı eylem linkleri"""
        user = self.request.user
        actions = []
        
        if user.is_doctor():
            actions = [
                {'title': 'Bugünün Randevuları', 'url': 'appointment-list', 'icon': 'calendar', 'color': 'primary'},
                {'title': 'Yeni Tedavi', 'url': 'treatment-create', 'icon': 'plus', 'color': 'success'},
                {'title': 'Lab Test İste', 'url': 'lab-test-create', 'icon': 'flask', 'color': 'info'},
                {'title': 'Hasta Arama', 'url': 'patient-search', 'icon': 'search', 'color': 'warning'},
            ]
        elif user.is_patient():
            actions = [
                {'title': 'Randevu Al', 'url': 'appointment-create', 'icon': 'calendar-plus', 'color': 'primary'},
                {'title': 'Tedavi Geçmişi', 'url': 'patient-treatment-history', 'icon': 'history', 'color': 'info'},
                {'title': 'Test Sonuçları', 'url': 'patient-lab-results', 'icon': 'chart-bar', 'color': 'success'},
                {'title': 'Reçetelerim', 'url': 'patient-prescriptions', 'icon': 'pills', 'color': 'warning'},
            ]
        elif user.is_receptionist():
            actions = [
                {'title': 'Yeni Randevu', 'url': 'appointment-create', 'icon': 'calendar-plus', 'color': 'primary'},
                {'title': 'Hasta Kaydı', 'url': 'patient-register', 'icon': 'user-plus', 'color': 'success'},
                {'title': 'Randevu Listesi', 'url': 'appointment-list', 'icon': 'list', 'color': 'info'},
                {'title': 'Doktor Takvimi', 'url': 'doctor-calendar', 'icon': 'calendar', 'color': 'warning'},
            ]
        elif user.is_admin_user():
            actions = [
                {'title': 'Sistem Raporları', 'url': 'system-reports', 'icon': 'chart-line', 'color': 'primary'},
                {'title': 'Kullanıcı Yönetimi', 'url': 'user-management', 'icon': 'users', 'color': 'success'},
                {'title': 'Sistem Ayarları', 'url': 'system-settings', 'icon': 'cog', 'color': 'info'},
                {'title': 'Veritabanı Bakımı', 'url': 'database-maintenance', 'icon': 'database', 'color': 'warning'},
            ]
        
        return actions
    
    def get_recent_activities(self):
        """Son aktiviteler"""
        user = self.request.user
        activities = []
        
        if user.is_doctor():
            # Son randevuları
            recent_appointments = Appointment.objects.filter(
                doctor=user,
                date__gte=timezone.now().date() - timedelta(days=7)
            ).order_by('-date', '-time')[:5]
            
            for appointment in recent_appointments:
                activities.append({
                    'type': 'appointment',
                    'title': f'{appointment.patient.get_full_name()} ile randevu',
                    'date': appointment.date,
                    'time': appointment.time,
                    'status': appointment.status,
                    'url': f'/appointments/{appointment.id}/',
                })
            
            # Son tedaviler
            recent_treatments = Treatment.objects.filter(
                appointment__doctor=user
            ).order_by('-created_at')[:3]
            
            for treatment in recent_treatments:
                activities.append({
                    'type': 'treatment',
                    'title': f'{treatment.appointment.patient.get_full_name()} tedavisi',
                    'date': treatment.created_at.date(),
                    'description': treatment.diagnosis[:50] + '...' if len(treatment.diagnosis) > 50 else treatment.diagnosis,
                    'url': f'/treatments/{treatment.id}/',
                })
        
        elif user.is_patient():
            # Son randevuları
            recent_appointments = Appointment.objects.filter(
                patient=user
            ).order_by('-date', '-time')[:5]
            
            for appointment in recent_appointments:
                activities.append({
                    'type': 'appointment',
                    'title': f'Dr. {appointment.doctor.get_full_name()} ile randevu',
                    'date': appointment.date,
                    'time': appointment.time,
                    'status': appointment.status,
                    'url': f'/appointments/{appointment.id}/',
                })
            
            # Bekleyen test sonuçları
            pending_tests = LabTest.objects.filter(
                patient=user,
                status__in=['requested', 'in_progress']
            ).order_by('-requested_date')[:3]
            
            for test in pending_tests:
                activities.append({
                    'type': 'lab_test',
                    'title': f'{test.test_name} - Test bekleniyor',
                    'date': test.requested_date.date(),
                    'status': test.status,
                    'url': f'/lab-tests/{test.id}/',
                })
        
        # Tarihe göre sırala
        activities.sort(key=lambda x: x.get('date', timezone.now().date()), reverse=True)
        
        return activities[:8]  # En son 8 aktivite


@login_required
def dashboard_analytics_api(request):
    """
    Dashboard için AJAX API endpoint
    """
    date_range = request.GET.get('range', 30)
    try:
        date_range = int(date_range)
    except ValueError:
        date_range = 30
    
    analytics = DashboardAnalytics(user=request.user, date_range_days=date_range)
    data = analytics.get_comprehensive_dashboard_data()
    
    return JsonResponse(data)


@login_required
def patient_health_summary_api(request, patient_id):
    """
    Hasta sağlık özeti API
    """
    if not (request.user.is_doctor() or request.user.is_admin_user()):
        return JsonResponse({'error': 'Yetkisiz erişim'}, status=403)
    
    patient = get_object_or_404(User, id=patient_id, user_type='patient')
    summary = ReportGenerator.generate_patient_health_summary(patient)
    
    # Django modellerini JSON'a çevir
    def model_to_dict(instance):
        if hasattr(instance, '_meta'):
            data = {}
            for field in instance._meta.fields:
                value = getattr(instance, field.name)
                if hasattr(value, 'isoformat'):  # Tarih/saat alanları
                    data[field.name] = value.isoformat()
                elif hasattr(value, '__str__'):
                    data[field.name] = str(value)
                else:
                    data[field.name] = value
            return data
        return str(instance)
    
    # Modelleri serileştir
    serialized_summary = {}
    for key, value in summary.items():
        if key == 'patient':
            serialized_summary[key] = {
                'id': value.id,
                'full_name': value.get_full_name(),
                'username': value.username,
                'email': value.email
            }
        elif hasattr(value, '__iter__') and not isinstance(value, str):
            serialized_summary[key] = [model_to_dict(item) for item in value]
        else:
            serialized_summary[key] = model_to_dict(value) if hasattr(value, '_meta') else value
    
    return JsonResponse(serialized_summary)


class DoctorPerformanceView(LoginRequiredMixin, TemplateView):
    """
    Doktor performans dashboard'u
    """
    template_name = 'dashboards/doctor_performance.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_doctor():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Bu sayfaya sadece doktorlar erişebilir.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Farklı zaman aralıkları için performans verileri
        periods = [
            ('Bu Hafta', 7),
            ('Bu Ay', 30),
            ('Son 3 Ay', 90),
            ('Bu Yıl', 365)
        ]
        
        performance_data = {}
        for period_name, days in periods:
            analytics = DashboardAnalytics(user=self.request.user, date_range_days=days)
            performance_data[period_name] = analytics.get_doctor_performance()
        
        context['performance_data'] = performance_data
        context['doctor'] = self.request.user
        
        # Hasta memnuniyet verileri (gelecekte eklenebilir)
        context['satisfaction_ratings'] = self.get_satisfaction_data()
        
        return context
    
    def get_satisfaction_data(self):
        """Hasta memnuniyet verileri (placeholder)"""
        # Bu gelecekte gerçek verilerle doldurulabilir
        return {
            'average_rating': 4.8,
            'total_reviews': 156,
            'rating_distribution': {
                '5': 78,
                '4': 52,
                '3': 18,
                '2': 6,
                '1': 2
            }
        }


class SystemReportsView(LoginRequiredMixin, TemplateView):
    """
    Sistem raporları (sadece admin)
    """
    template_name = 'dashboards/system_reports.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin_user():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Bu sayfaya sadece adminler erişebilir.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sistem geneli istatistikler
        context['system_stats'] = {
            'total_users': User.objects.count(),
            'total_doctors': User.objects.filter(user_type='doctor').count(),
            'total_patients': User.objects.filter(user_type='patient').count(),
            'total_appointments': Appointment.objects.count(),
            'total_treatments': Treatment.objects.count(),
            'total_lab_tests': LabTest.objects.count(),
        }
        
        # En aktif doktorlar
        context['top_doctors'] = User.objects.filter(
            user_type='doctor'
        ).annotate(
            appointment_count=Count('doctor_appointments')
        ).order_by('-appointment_count')[:10]
        
        # Aylık büyüme verileri
        context['monthly_growth'] = self.get_monthly_growth_data()
        
        return context
    
    def get_monthly_growth_data(self):
        """Aylık büyüme verilerini hesapla"""
        months_data = []
        
        for i in range(12):  # Son 12 ay
            month_date = timezone.now().date().replace(day=1) - timedelta(days=i*30)
            month_start = month_date.replace(day=1)
            
            # Ay sonu hesapla
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            new_users = User.objects.filter(
                date_joined__date__range=[month_start, month_end]
            ).count()
            
            new_appointments = Appointment.objects.filter(
                created_at__date__range=[month_start, month_end]
            ).count()
            
            months_data.append({
                'month': month_start.strftime('%B %Y'),
                'new_users': new_users,
                'new_appointments': new_appointments
            })
        
        return list(reversed(months_data))
