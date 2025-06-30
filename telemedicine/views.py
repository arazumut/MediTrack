"""
Telemedicine Views for MediTracked
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import models
import json
import uuid
import time
from datetime import datetime

from .models import TeleMedicineConsultation, TeleMedicineMessage, TeleMedicineSettings, TelemedicineAppointment, VideoSession, TelemedDocument, TelemedPrescription, TelemedNote
from appointments.models import Appointment
from core.models_notifications import Notification, NotificationType
from .forms import TelemedicineAppointmentForm, TelemedDocumentForm, TelemedPrescriptionForm, TelemedNoteForm


class TeleMedicineConsultationListView(LoginRequiredMixin, ListView):
    """
    Telemedicine konsültasyon listesi
    """
    model = TeleMedicineConsultation
    template_name = 'telemedicine/consultation_list.html'
    context_object_name = 'consultations'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_doctor():
            return TeleMedicineConsultation.objects.filter(
                appointment__doctor=user
            ).order_by('-scheduled_start_time')
        elif user.is_patient():
            return TeleMedicineConsultation.objects.filter(
                appointment__patient=user
            ).order_by('-scheduled_start_time')
        else:
            return TeleMedicineConsultation.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Bugünkü konsültasyonlar
        today_consultations = self.get_queryset().filter(
            scheduled_start_time__date=timezone.now().date()
        )
        
        context['today_consultations'] = today_consultations
        context['upcoming_count'] = self.get_queryset().filter(
            status='scheduled',
            scheduled_start_time__gt=timezone.now()
        ).count()
        
        return context


class TeleMedicineConsultationDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Telemedicine konsültasyon detayı
    """
    model = TeleMedicineConsultation
    template_name = 'telemedicine/consultation_detail.html'
    context_object_name = 'consultation'
    
    def test_func(self):
        consultation = self.get_object()
        user = self.request.user
        
        # Sadece doktor ve hasta erişebilir
        return user in [consultation.appointment.doctor, consultation.appointment.patient]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultation = self.get_object()
        
        # Chat mesajları
        context['chat_messages'] = consultation.chat_messages.all()
        
        # Kullanıcı katılabilir mi?
        context['can_join'] = consultation.can_join(self.request.user)
        context['join_url'] = consultation.get_join_url()
        
        # Konsültasyon durumu
        context['is_active'] = consultation.is_active()
        context['time_until_start'] = None
        
        if consultation.scheduled_start_time > timezone.now():
            context['time_until_start'] = consultation.scheduled_start_time - timezone.now()
        
        return context


@login_required
@require_http_methods(["POST"])
def create_telemedicine_consultation(request, appointment_id):
    """
    Randevu için telemedicine konsültasyonu oluştur
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Sadece doktor oluşturabilir
    if not request.user.is_doctor() or appointment.doctor != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Zaten konsültasyon var mı?
    if hasattr(appointment, 'telemedicine_consultation'):
        return JsonResponse({'error': 'Consultation already exists'}, status=400)
    
    try:
        data = json.loads(request.body)
        consultation_type = data.get('consultation_type', 'video')
        
        # Konsültasyon oluştur
        consultation = TeleMedicineConsultation.objects.create(
            appointment=appointment,
            consultation_type=consultation_type,
            scheduled_start_time=timezone.make_aware(
                timezone.datetime.combine(appointment.date, appointment.time)
            ),
            platform='internal'
        )
        
        # Hastaya bildirim gönder
        Notification.objects.create(
            recipient=appointment.patient,
            sender=request.user,
            notification_type=NotificationType.APPOINTMENT_CONFIRMED,
            title=_('Telemedicine Randevusu Oluşturuldu'),
            message=_(f'Dr. {request.user.get_full_name()} ile {appointment.date} tarihli randevunuz için online konsültasyon hazırlandı.'),
            related_object=consultation
        )
        
        return JsonResponse({
            'success': True,
            'consultation_id': consultation.id,
            'meeting_id': str(consultation.meeting_id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def join_consultation(request, meeting_id):
    """
    Konsültasyona katıl
    """
    consultation = get_object_or_404(TeleMedicineConsultation, meeting_id=meeting_id)
    
    # Kullanıcı katılabilir mi?
    if not consultation.can_join(request.user):
        messages.error(request, _('Bu konsültasyona katılma yetkiniz yok.'))
        return redirect('telemedicine-consultation-list')
    
    # Konsültasyonu başlat
    consultation.mark_as_started(request.user)
    
    # Konsültasyon odasına yönlendir
    return render(request, 'telemedicine/consultation_room.html', {
        'consultation': consultation,
        'user_role': 'doctor' if request.user.is_doctor() else 'patient',
        'is_doctor': request.user.is_doctor(),
        'is_patient': request.user.is_patient()
    })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def send_consultation_message(request, consultation_id):
    """
    Konsültasyon sırasında mesaj gönder
    """
    consultation = get_object_or_404(TeleMedicineConsultation, id=consultation_id)
    
    # Erişim kontrolü
    if not consultation.can_join(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        message_type = data.get('type', 'text')
        
        if not content:
            return JsonResponse({'error': 'Message content required'}, status=400)
        
        # Mesaj oluştur
        message = TeleMedicineMessage.objects.create(
            consultation=consultation,
            sender=request.user,
            message_type=message_type,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': message.sender.get_full_name(),
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'type': message.message_type
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_consultation_messages(request, consultation_id):
    """
    Konsültasyon mesajlarını al
    """
    consultation = get_object_or_404(TeleMedicineConsultation, id=consultation_id)
    
    # Erişim kontrolü
    if not consultation.can_join(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    messages = consultation.chat_messages.all().order_by('timestamp')
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'sender': message.sender.get_full_name(),
            'sender_id': message.sender.id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'type': message.message_type,
            'is_own': message.sender == request.user
        })
    
    return JsonResponse({
        'messages': messages_data
    })


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def end_consultation(request, consultation_id):
    """
    Konsültasyonu sonlandır
    """
    consultation = get_object_or_404(TeleMedicineConsultation, id=consultation_id)
    
    # Sadece doktor sonlandırabilir
    if not request.user.is_doctor() or consultation.appointment.doctor != request.user:
        return JsonResponse({'error': 'Only doctor can end consultation'}, status=403)
    
    try:
        data = json.loads(request.body)
        consultation_notes = data.get('notes', '')
        patient_feedback = data.get('patient_feedback', '')
        
        # Konsültasyonu sonlandır
        consultation.mark_as_completed()
        consultation.consultation_notes = consultation_notes
        consultation.patient_feedback = patient_feedback
        consultation.save()
        
        # Randevuyu tamamla
        appointment = consultation.appointment
        appointment.status = 'completed'
        appointment.save()
        
        # Hasta ve doktora bildirim gönder
        Notification.objects.create(
            recipient=appointment.patient,
            sender=request.user,
            notification_type=NotificationType.TREATMENT_COMPLETED,
            title=_('Telemedicine Konsültasyonu Tamamlandı'),
            message=_(f'Dr. {request.user.get_full_name()} ile online konsültasyonunuz tamamlandı.'),
            related_object=consultation
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Consultation ended successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required 
@require_http_methods(["POST"])
def update_consultation_status(request, consultation_id):
    """
    Konsültasyon durumunu güncelle
    """
    consultation = get_object_or_404(TeleMedicineConsultation, id=consultation_id)
    
    # Erişim kontrolü
    if not consultation.can_join(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        status = data.get('status')
        connection_quality = data.get('connection_quality')
        technical_issues = data.get('technical_issues', '')
        
        if status and status in dict(TeleMedicineConsultation.STATUS_CHOICES):
            consultation.status = status
        
        if connection_quality:
            consultation.connection_quality = connection_quality
        
        if technical_issues:
            consultation.technical_issues = technical_issues
        
        consultation.save()
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class TeleMedicineSettingsView(LoginRequiredMixin, UpdateView):
    """
    Telemedicine ayarları
    """
    model = TeleMedicineSettings
    template_name = 'telemedicine/settings.html'
    fields = [
        'default_camera_enabled', 'default_microphone_enabled', 'video_quality',
        'consultation_reminders', 'reminder_minutes_before', 'email_notifications',
        'sms_notifications', 'require_waiting_room', 'allow_recording',
        'allow_file_sharing', 'max_consultation_duration', 'auto_end_consultation'
    ]
    success_url = reverse_lazy('telemedicine-settings')
    
    def get_object(self, queryset=None):
        settings, created = TeleMedicineSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings
    
    def form_valid(self, form):
        messages.success(self.request, _('Telemedicine ayarları başarıyla güncellendi.'))
        return super().form_valid(form)


@login_required
@require_http_methods(["GET"])
def consultation_analytics(request):
    """
    Telemedicine analitikleri
    """
    if not request.user.is_doctor():
        return JsonResponse({'error': 'Only doctors can access analytics'}, status=403)
    
    # Son 30 gün
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=30)
    
    consultations = TeleMedicineConsultation.objects.filter(
        appointment__doctor=request.user,
        scheduled_start_time__date__range=[start_date, end_date]
    )
    
    analytics = {
        'total_consultations': consultations.count(),
        'completed_consultations': consultations.filter(status='completed').count(),
        'cancelled_consultations': consultations.filter(status='cancelled').count(),
        'average_duration': 0,
        'total_duration': 0,
        'patient_satisfaction': 0,
        'connection_quality_stats': {},
        'daily_stats': []
    }
    
    # Ortalama süre hesapla
    completed = consultations.filter(status='completed', duration_minutes__isnull=False)
    if completed.exists():
        total_duration = sum(c.duration_minutes for c in completed)
        analytics['total_duration'] = total_duration
        analytics['average_duration'] = total_duration / completed.count()
    
    # Hasta memnuniyeti
    rated_consultations = consultations.filter(patient_rating__isnull=False)
    if rated_consultations.exists():
        total_rating = sum(c.patient_rating for c in rated_consultations)
        analytics['patient_satisfaction'] = total_rating / rated_consultations.count()
    
    # Bağlantı kalitesi istatistikleri
    quality_stats = consultations.values('connection_quality').annotate(
        count=models.Count('connection_quality')
    )
    analytics['connection_quality_stats'] = {
        item['connection_quality']: item['count'] for item in quality_stats
    }
    
    return JsonResponse(analytics)


@login_required
def telemedicine_dashboard(request):
    """
    Telemedicine dashboard
    """
    user = request.user
    
    if user.is_doctor():
        # Doktor dashboard'u
        upcoming_consultations = TeleMedicineConsultation.objects.filter(
            appointment__doctor=user,
            status='scheduled',
            scheduled_start_time__gt=timezone.now()
        ).order_by('scheduled_start_time')[:5]
        
        today_consultations = TeleMedicineConsultation.objects.filter(
            appointment__doctor=user,
            scheduled_start_time__date=timezone.now().date()
        )
        
        context = {
            'upcoming_consultations': upcoming_consultations,
            'today_consultations': today_consultations,
            'today_count': today_consultations.count(),
            'user_type': 'doctor'
        }
        
    elif user.is_patient():
        # Hasta dashboard'u
        next_consultation = TeleMedicineConsultation.objects.filter(
            appointment__patient=user,
            status='scheduled',
            scheduled_start_time__gt=timezone.now()
        ).order_by('scheduled_start_time').first()
        
        recent_consultations = TeleMedicineConsultation.objects.filter(
            appointment__patient=user,
            status='completed'
        ).order_by('-scheduled_start_time')[:5]
        
        context = {
            'next_consultation': next_consultation,
            'recent_consultations': recent_consultations,
            'user_type': 'patient'
        }
    
    else:
        context = {'user_type': 'other'}
    
    return render(request, 'telemedicine/dashboard.html', context)


@login_required
def create_telemedicine_appointment(request):
    if request.method == 'POST':
        form = TelemedicineAppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # Kullanıcı tipine göre atama
            if request.user.is_patient():
                appointment.patient = request.user
            else:
                appointment.created_by = request.user
                
            appointment.save()
            
            # Doktor için bildirim oluştur
            Notification.objects.create(
                recipient=appointment.doctor,
                notification_type=NotificationType.APPOINTMENT_CONFIRMED,
                title="Yeni Tele-tıp Randevusu",
                message=f"{appointment.patient.get_full_name()} ile {appointment.date.strftime('%d.%m.%Y')} tarihinde saat {appointment.time.strftime('%H:%M')} için yeni bir tele-tıp randevunuz var.",
                priority="normal",
                extra_data={
                    "appointment_id": appointment.id,
                    "patient_id": appointment.patient.id,
                }
            )
            
            # Hasta için bildirim oluştur (hasta oluşturmadıysa)
            if not request.user.is_patient():
                Notification.objects.create(
                    recipient=appointment.patient,
                    notification_type=NotificationType.APPOINTMENT_CONFIRMED,
                    title="Yeni Tele-tıp Randevusu",
                    message=f"Dr. {appointment.doctor.get_full_name()} ile {appointment.date.strftime('%d.%m.%Y')} tarihinde saat {appointment.time.strftime('%H:%M')} için yeni bir tele-tıp randevunuz oluşturuldu.",
                    priority="normal",
                    extra_data={
                        "appointment_id": appointment.id,
                        "doctor_id": appointment.doctor.id,
                    }
                )
            
            messages.success(request, "Tele-tıp randevusu başarıyla oluşturuldu.")
            return redirect('telemedicine-appointment-detail', pk=appointment.pk)
    else:
        form = TelemedicineAppointmentForm(user=request.user)
        
    return render(request, 'telemedicine/appointment_form.html', {'form': form})


@login_required
def start_video_session(request, appointment_id):
    appointment = get_object_or_404(TelemedicineAppointment, id=appointment_id)
    
    # Yetki kontrolü
    if not (request.user == appointment.doctor or request.user == appointment.patient):
        messages.error(request, "Bu görüşmeye erişim yetkiniz yok.")
        return redirect('telemedicine-appointment-list')
    
    # Randevu zamanı kontrolü
    now = timezone.now()
    appointment_datetime = timezone.make_aware(datetime.combine(appointment.date, appointment.time))
    time_diff = (appointment_datetime - now).total_seconds() / 60  # Dakika cinsinden
    
    # Randevudan 10 dakika önce veya 30 dakika sonrasına kadar izin ver
    if time_diff > 10:
        messages.warning(request, f"Görüşme henüz başlamadı. Randevunuz {appointment.time.strftime('%H:%M')} saatinde.")
        return redirect('telemedicine-appointment-detail', pk=appointment_id)
    
    if time_diff < -30:
        messages.warning(request, "Bu randevunun süresi dolmuş. Yeni bir randevu oluşturun.")
        return redirect('telemedicine-appointment-list')
    
    # Aktif görüşme var mı kontrol et
    active_session = VideoSession.objects.filter(
        appointment=appointment,
        end_time__isnull=True
    ).first()
    
    # Yoksa yeni görüşme başlat
    if not active_session:
        active_session = VideoSession.objects.create(
            appointment=appointment,
            started_by=request.user,
            room_name=f"telemed_{appointment.id}_{int(time.time())}"
        )
        
        # Karşı tarafa bildirim gönder
        recipient = appointment.patient if request.user == appointment.doctor else appointment.doctor
        Notification.objects.create(
            recipient=recipient,
            notification_type=NotificationType.APPOINTMENT_REMINDER,
            title="Görüşme Başladı",
            message=f"{request.user.get_full_name()} görüşmeyi başlattı. Şimdi katılabilirsiniz.",
            priority="high",
            extra_data={
                "appointment_id": appointment.id,
                "session_id": active_session.id,
            }
        )
    
    # Görüşme sayfasına yönlendir
    return render(request, 'telemedicine/video_session.html', {
        'appointment': appointment,
        'session': active_session,
        'is_doctor': request.user == appointment.doctor
    })


@login_required
def end_video_session(request, session_id):
    session = get_object_or_404(VideoSession, id=session_id)
    appointment = session.appointment
    
    # Yetki kontrolü
    if not (request.user == appointment.doctor or request.user == appointment.patient):
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return JsonResponse({'status': 'error', 'message': 'Yetki hatası'})
    
    # Görüşmeyi sonlandır
    if not session.end_time:
        session.end_time = timezone.now()
        session.ended_by = request.user
        session.save()
    
    return JsonResponse({'status': 'success'})


class TelemedicineAppointmentListView(LoginRequiredMixin, ListView):
    model = TelemedicineAppointment
    template_name = 'telemedicine/appointment_list.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        user = self.request.user
        queryset = TelemedicineAppointment.objects.all()
        
        # Kullanıcı tipine göre filtrele
        if user.is_patient():
            queryset = queryset.filter(patient=user)
        elif user.is_doctor():
            queryset = queryset.filter(doctor=user)
        
        # Durum filtresi
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Tarih filtresi
        date_filter = self.request.GET.get('date_filter', 'upcoming')
        today = timezone.now().date()
        
        if date_filter == 'upcoming':
            queryset = queryset.filter(date__gte=today)
        elif date_filter == 'past':
            queryset = queryset.filter(date__lt=today)
        
        return queryset.order_by('date', 'time')


class TelemedicineAppointmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = TelemedicineAppointment
    template_name = 'telemedicine/appointment_detail.html'
    context_object_name = 'appointment'
    
    def test_func(self):
        appointment = self.get_object()
        user = self.request.user
        return (user == appointment.doctor or 
                user == appointment.patient or 
                user.is_receptionist() or 
                user.is_admin_user())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = self.get_object()
        
        # Belgeleri ekle
        context['documents'] = TelemedDocument.objects.filter(appointment=appointment)
        
        # Reçeteleri ekle
        context['prescriptions'] = TelemedPrescription.objects.filter(appointment=appointment)
        
        # Notları ekle
        context['notes'] = TelemedNote.objects.filter(appointment=appointment)
        
        # Görüşme geçmişini ekle
        context['sessions'] = VideoSession.objects.filter(appointment=appointment)
        
        # Aktif görüşme var mı?
        context['active_session'] = VideoSession.objects.filter(
            appointment=appointment,
            end_time__isnull=True
        ).first()
        
        # Formları ekle
        if self.request.user == appointment.doctor:
            context['document_form'] = TelemedDocumentForm()
            context['prescription_form'] = TelemedPrescriptionForm()
            context['note_form'] = TelemedNoteForm()
        
        return context
