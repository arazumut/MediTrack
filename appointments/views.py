from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from .models import Appointment

User = get_user_model()

# Create your views here.

# Takvim Görünümü
class CalendarView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/calendar.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        user = self.request.user
        
        # Tarih filtresi
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if not start_date:
            # Varsayılan olarak bu ayın başlangıcı
            today = timezone.now().date()
            start_date = today.replace(day=1)
        else:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            # Varsayılan olarak bir sonraki ayın başlangıcı
            next_month = start_date.month + 1 if start_date.month < 12 else 1
            next_year = start_date.year + 1 if start_date.month == 12 else start_date.year
            end_date = start_date.replace(year=next_year, month=next_month, day=1) - timedelta(days=1)
        else:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        queryset = Appointment.objects.filter(date__range=[start_date, end_date])
        
        # Kullanıcı tipine göre filtrele
        if user.is_patient():
            queryset = queryset.filter(patient=user)
        elif user.is_doctor():
            queryset = queryset.filter(doctor=user)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Doktor listesi
        context['doctors'] = User.objects.filter(user_type='doctor')
        
        # Takvim verisi
        calendar_data = []
        for appointment in self.get_queryset():
            calendar_data.append({
                'id': appointment.id,
                'title': f"{appointment.patient.get_full_name()} - Dr. {appointment.doctor.get_full_name()}",
                'start': f"{appointment.date.isoformat()}T{appointment.time.isoformat()}",
                'end': f"{appointment.date.isoformat()}T{(appointment.time.replace(hour=appointment.time.hour+1)).isoformat()}",
                'url': f"/appointments/{appointment.id}/",
                'backgroundColor': self.get_status_color(appointment.status),
                'borderColor': self.get_status_color(appointment.status),
            })
        
        context['calendar_data'] = calendar_data
        
        return context
    
    def get_status_color(self, status):
        """Randevu durumuna göre renk döndürür"""
        colors = {
            'planned': '#3699FF',  # Mavi
            'completed': '#1BC5BD',  # Yeşil
            'cancelled': '#F64E60',  # Kırmızı
        }
        return colors.get(status, '#3699FF')

# AJAX ile randevu verilerini getiren görünüm
def get_calendar_events(request):
    user = request.user
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date and end_date:
        start_date = timezone.datetime.strptime(start_date.split('T')[0], '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date.split('T')[0], '%Y-%m-%d').date()
        
        queryset = Appointment.objects.filter(date__range=[start_date, end_date])
        
        # Kullanıcı tipine göre filtrele
        if user.is_patient():
            queryset = queryset.filter(patient=user)
        elif user.is_doctor():
            queryset = queryset.filter(doctor=user)
        
        events = []
        for appointment in queryset:
            events.append({
                'id': appointment.id,
                'title': f"{appointment.patient.get_full_name()} - Dr. {appointment.doctor.get_full_name()}",
                'start': f"{appointment.date.isoformat()}T{appointment.time.isoformat()}",
                'end': f"{appointment.date.isoformat()}T{(appointment.time.replace(hour=appointment.time.hour+1)).isoformat()}",
                'url': f"/appointments/{appointment.id}/",
                'backgroundColor': get_status_color(appointment.status),
                'borderColor': get_status_color(appointment.status),
            })
        
        return JsonResponse(events, safe=False)
    
    return JsonResponse([], safe=False)

def get_status_color(status):
    """Randevu durumuna göre renk döndürür"""
    colors = {
        'planned': '#3699FF',  # Mavi
        'completed': '#1BC5BD',  # Yeşil
        'cancelled': '#F64E60',  # Kırmızı
    }
    return colors.get(status, '#3699FF')
