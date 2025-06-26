"""
Mobile API Endpoints for MediTracked
REST API for mobile applications
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
import json

from appointments.models import Appointment
from treatments.models import Treatment, Prescription
from treatments.models_lab import LabTest
from treatments.models_medical_history import MedicalHistory
from core.models_notifications import Notification
from core.ai_features import AIHealthInsights
from django.contrib.auth import get_user_model

User = get_user_model()


class MobileAPIResponse:
    """Mobil API yanıtları için yardımcı sınıf"""
    
    @staticmethod
    def success(data=None, message="Success"):
        return JsonResponse({
            'success': True,
            'message': message,
            'data': data,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def error(message="Error occurred", error_code=400):
        return JsonResponse({
            'success': False,
            'message': message,
            'error_code': error_code,
            'timestamp': timezone.now().isoformat()
        }, status=error_code)


@csrf_exempt
@require_http_methods(["POST"])
def mobile_login(request):
    """
    Mobil giriş API
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return MobileAPIResponse.error("Username and password required", 400)
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return MobileAPIResponse.success({
                'user_id': user.id,
                'username': user.username,
                'full_name': user.get_full_name(),
                'user_type': user.user_type,
                'email': user.email,
                'session_token': request.session.session_key
            }, "Login successful")
        else:
            return MobileAPIResponse.error("Invalid credentials", 401)
    
    except json.JSONDecodeError:
        return MobileAPIResponse.error("Invalid JSON", 400)
    except Exception as e:
        return MobileAPIResponse.error(f"Server error: {str(e)}", 500)


@login_required
@require_http_methods(["GET"])
def mobile_dashboard(request):
    """
    Mobil dashboard verisi
    """
    try:
        user = request.user
        
        # Kullanıcı tipine göre farklı veriler
        if user.is_patient():
            # Hasta dashboard'u
            next_appointment = Appointment.objects.filter(
                patient=user,
                date__gte=timezone.now().date(),
                status='planned'
            ).order_by('date', 'time').first()
            
            recent_treatments = Treatment.objects.filter(
                appointment__patient=user
            ).order_by('-created_at')[:3]
            
            pending_tests = LabTest.objects.filter(
                patient=user,
                status__in=['requested', 'in_progress']
            ).count()
            
            unread_notifications = Notification.objects.filter(
                recipient=user,
                is_read=False
            ).count()
            
            dashboard_data = {
                'next_appointment': {
                    'date': next_appointment.date.isoformat() if next_appointment else None,
                    'time': next_appointment.time.strftime('%H:%M') if next_appointment else None,
                    'doctor': next_appointment.doctor.get_full_name() if next_appointment else None
                } if next_appointment else None,
                'recent_treatments_count': recent_treatments.count(),
                'pending_tests_count': pending_tests,
                'unread_notifications': unread_notifications,
                'quick_actions': [
                    {'title': 'Randevu Al', 'action': 'book_appointment', 'icon': 'calendar'},
                    {'title': 'Test Sonuçları', 'action': 'view_lab_results', 'icon': 'flask'},
                    {'title': 'Reçeteler', 'action': 'view_prescriptions', 'icon': 'pills'},
                    {'title': 'Doktor Ara', 'action': 'find_doctor', 'icon': 'search'}
                ]
            }
        
        elif user.is_doctor():
            # Doktor dashboard'u
            today_appointments = Appointment.objects.filter(
                doctor=user,
                date=timezone.now().date()
            ).count()
            
            pending_treatments = Appointment.objects.filter(
                doctor=user,
                status='completed'
            ).exclude(treatment__isnull=False).count()
            
            dashboard_data = {
                'today_appointments': today_appointments,
                'pending_treatments': pending_treatments,
                'quick_actions': [
                    {'title': 'Bugünün Randevuları', 'action': 'today_appointments', 'icon': 'calendar'},
                    {'title': 'Hasta Arama', 'action': 'search_patient', 'icon': 'search'},
                    {'title': 'Yeni Tedavi', 'action': 'new_treatment', 'icon': 'plus'},
                    {'title': 'Lab Test İste', 'action': 'order_lab_test', 'icon': 'flask'}
                ]
            }
        
        else:
            # Diğer kullanıcı tipleri için genel dashboard
            dashboard_data = {
                'message': 'Welcome to MediTracked',
                'user_type': user.user_type
            }
        
        return MobileAPIResponse.success(dashboard_data)
    
    except Exception as e:
        return MobileAPIResponse.error(f"Server error: {str(e)}", 500)


@login_required
@require_http_methods(["GET"])
def mobile_appointments(request):
    """
    Mobil randevu listesi
    """
    try:
        user = request.user
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        
        if user.is_patient():
            appointments = Appointment.objects.filter(patient=user)
        elif user.is_doctor():
            appointments = Appointment.objects.filter(doctor=user)
        else:
            return MobileAPIResponse.error("Unauthorized", 403)
        
        appointments = appointments.order_by('-date', '-time')
        
        paginator = Paginator(appointments, limit)
        page_obj = paginator.get_page(page)
        
        appointments_data = []
        for appointment in page_obj:
            appointments_data.append({
                'id': appointment.id,
                'date': appointment.date.isoformat(),
                'time': appointment.time.strftime('%H:%M'),
                'status': appointment.status,
                'patient_name': appointment.patient.get_full_name() if user.is_doctor() else None,
                'doctor_name': appointment.doctor.get_full_name() if user.is_patient() else None,
                'description': appointment.description,
                'has_treatment': hasattr(appointment, 'treatment')
            })
        
        return MobileAPIResponse.success({
            'appointments': appointments_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page
        })
    
    except Exception as e:
        return MobileAPIResponse.error(f"Server error: {str(e)}", 500)


@login_required
@require_http_methods(["GET"])
def mobile_notifications(request):
    """
    Mobil bildirimler
    """
    try:
        user = request.user
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
        
        notifications = Notification.objects.filter(recipient=user)
        
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        notifications = notifications.order_by('-created_at')[:20]
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'icon': notification.get_icon(),
                'color': notification.get_priority_color()
            })
        
        return MobileAPIResponse.success({
            'notifications': notifications_data,
            'unread_count': Notification.objects.filter(recipient=user, is_read=False).count()
        })
    
    except Exception as e:
        return MobileAPIResponse.error(f"Server error: {str(e)}", 500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def mobile_mark_notification_read(request, notification_id):
    """
    Bildirimi okundu olarak işaretle
    """
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        
        notification.mark_as_read()
        
        return MobileAPIResponse.success(
            {'notification_id': notification_id, 'is_read': True},
            "Notification marked as read"
        )
    
    except Exception as e:
        return MobileAPIResponse.error(f"Server error: {str(e)}", 500)


@login_required
@require_http_methods(["GET"])
def mobile_health_summary(request):
    """
    Mobil sağlık özeti (sadece hastalar için)
    """
    try:
        user = request.user
        
        if not user.is_patient():
            return MobileAPIResponse.error("Only patients can access health summary", 403)
        
        # AI insights kullan
        ai_insights = AIHealthInsights()
        insights = ai_insights.generate_patient_insights(user)
        
        # Son lab testleri
        recent_tests = LabTest.objects.filter(
            patient=user,
            status='completed'
        ).order_by('-completed_date')[:5]
        
        tests_data = []
        for test in recent_tests:
            tests_data.append({
                'test_name': test.test_name,
                'completed_date': test.completed_date.isoformat() if test.completed_date else None,
                'status': test.status
            })
        
        # Aktif ilaçlar
        active_medications = MedicalHistory.objects.filter(
            patient=user,
            condition_type='medication',
            is_active=True
        )
        
        medications_data = []
        for med in active_medications:
            medications_data.append({
                'name': med.condition_name,
                'start_date': med.diagnosed_date.isoformat() if med.diagnosed_date else None,
                'notes': med.notes
            })
        
        health_summary = {
            'risk_assessment': insights['risk_assessment'],
            'recent_tests': tests_data,
            'active_medications': medications_data,
            'upcoming_care': insights['upcoming_care_suggestions'],
            'last_appointment': None
        }
        
        # Son randevu
        last_appointment = Appointment.objects.filter(
            patient=user,
            status='completed'
        ).order_by('-date').first()
        
        if last_appointment:
            health_summary['last_appointment'] = {
                'date': last_appointment.date.isoformat(),
                'doctor': last_appointment.doctor.get_full_name(),
                'has_treatment': hasattr(last_appointment, 'treatment')
            }
        
        return MobileAPIResponse.success(health_summary)
    
    except Exception as e:
        return MobileAPIResponse.error(f"Server error: {str(e)}", 500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def mobile_symptom_checker(request):
    """
    Mobil semptom kontrol API
    """
    try:
        data = json.loads(request.body)
        symptoms = data.get('symptoms', '')
        
        if not symptoms:
            return MobileAPIResponse.error("Symptoms required", 400)
        
        # AI semptom analizi
        from core.ai_features import SymptomAnalyzer
        analyzer = SymptomAnalyzer()
        analysis = analyzer.analyze_symptoms(symptoms)
        
        # Önerilen lab testleri
        from core.ai_features import TreatmentRecommendationEngine
        treatment_engine = TreatmentRecommendationEngine()
        recommended_tests = treatment_engine.recommend_lab_tests(symptoms)
        
        result = {
            'symptom_analysis': analysis,
            'recommended_tests': recommended_tests,
            'warning': 'Bu analiz sadece bilgilendirme amaçlıdır. Ciddi semptomlarınız varsa lütfen doktora başvurun.'
        }
        
        return MobileAPIResponse.success(result)
    
    except json.JSONDecodeError:
        return MobileAPIResponse.error("Invalid JSON", 400)
    except Exception as e:
        return MobileAPIResponse.error(f"Server error: {str(e)}", 500)


@login_required
@require_http_methods(["GET"])
def mobile_doctor_search(request):
    """
    Doktor arama API
    """
    try:
        search_query = request.GET.get('q', '')
        specialty = request.GET.get('specialty', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        
        doctors = User.objects.filter(user_type='doctor')
        
        if search_query:
            doctors = doctors.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query)
            )
        
        # Uzmanlık alanı filtresi (gelecekte eklenebilir)
        # if specialty:
        #     doctors = doctors.filter(specialty__icontains=specialty)
        
        paginator = Paginator(doctors, limit)
        page_obj = paginator.get_page(page)
        
        doctors_data = []
        for doctor in page_obj:
            # Doktorun müsaitlik durumunu kontrol et
            next_available = get_next_available_slot(doctor)
            
            doctors_data.append({
                'id': doctor.id,
                'name': doctor.get_full_name(),
                'username': doctor.username,
                'email': doctor.email,
                'next_available': next_available,
                'rating': 4.8,  # Placeholder - gelecekte gerçek rating sistemi
                'total_reviews': 156  # Placeholder
            })
        
        return MobileAPIResponse.success({
            'doctors': doctors_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page
        })
    
    except Exception as e:
        return MobileAPIResponse.error(f"Server error: {str(e)}", 500)


def get_next_available_slot(doctor):
    """Doktorun bir sonraki müsait slot'ını bul"""
    # Bu fonksiyon doktor takvim sistemi ile entegre edilebilir
    # Şimdilik basit bir örnek
    next_week = timezone.now().date() + timedelta(days=7)
    return next_week.isoformat()


# API endpoint'leri listesi
mobile_api_urls = [
    ('api/mobile/login/', mobile_login),
    ('api/mobile/dashboard/', mobile_dashboard),
    ('api/mobile/appointments/', mobile_appointments),
    ('api/mobile/notifications/', mobile_notifications),
    ('api/mobile/notifications/<int:notification_id>/read/', mobile_mark_notification_read),
    ('api/mobile/health-summary/', mobile_health_summary),
    ('api/mobile/symptom-checker/', mobile_symptom_checker),
    ('api/mobile/doctors/search/', mobile_doctor_search),
]
