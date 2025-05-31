from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView, TemplateView
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.utils import timezone

from .forms import (
    LoginForm, PatientRegistrationForm, AppointmentForm, 
    TreatmentForm, PrescriptionFormSet, DoctorCreationForm, DoctorUpdateForm
)
from appointments.models import Appointment
from treatments.models import Treatment, Prescription

User = get_user_model()

# Create your views here.

# Ana Sayfa
class HomeView(TemplateView):
    """
    Ana sayfa görünümü
    """
    template_name = 'core/index.html'

# Dashboard
@login_required
def dashboard(request):
    """
    Kullanıcı rolüne göre dashboard görünümü sağlar
    """
    user = request.user
    context = {'user': user}
    
    if user.is_patient():
        # Hasta dashboard'u
        upcoming_appointments = Appointment.objects.filter(
            patient=user,
            date__gte=timezone.now().date(),
            status='planned'
        ).order_by('date', 'time')
        
        recent_treatments = Treatment.objects.filter(
            appointment__patient=user
        ).order_by('-created_at')[:5]
        
        context.update({
            'upcoming_appointments': upcoming_appointments,
            'recent_treatments': recent_treatments,
        })
        return render(request, 'core/patient_dashboard.html', context)
    
    elif user.is_doctor():
        # Doktor dashboard'u
        today_appointments = Appointment.objects.filter(
            doctor=user,
            date=timezone.now().date(),
            status='planned'
        ).order_by('time')
        
        upcoming_appointments = Appointment.objects.filter(
            doctor=user,
            date__gt=timezone.now().date(),
            status='planned'
        ).order_by('date', 'time')[:5]
        
        recent_treatments = Treatment.objects.filter(
            appointment__doctor=user
        ).order_by('-created_at')[:5]
        
        context.update({
            'today_appointments': today_appointments,
            'upcoming_appointments': upcoming_appointments,
            'recent_treatments': recent_treatments,
        })
        return render(request, 'core/doctor_dashboard.html', context)
    
    elif user.is_receptionist():
        # Resepsiyonist dashboard'u
        today_appointments = Appointment.objects.filter(
            date=timezone.now().date()
        ).order_by('time')
        
        recent_patients = User.objects.filter(
            user_type='patient'
        ).order_by('-date_joined')[:5]
        
        context.update({
            'today_appointments': today_appointments,
            'recent_patients': recent_patients,
        })
        return render(request, 'core/receptionist_dashboard.html', context)
    
    elif user.is_admin_user() or user.is_superuser:
        # Admin dashboard'u
        total_patients = User.objects.filter(user_type='patient').count()
        total_doctors = User.objects.filter(user_type='doctor').count()
        total_appointments = Appointment.objects.count()
        total_treatments = Treatment.objects.count()
        
        context.update({
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_appointments': total_appointments,
            'total_treatments': total_treatments,
        })
        return render(request, 'core/admin_dashboard.html', context)
    
    # Varsayılan olarak genel dashboard'a yönlendir
    return render(request, 'core/dashboard.html', context)

# Hasta Kayıt
class PatientRegistrationView(CreateView):
    """
    Yeni hasta kaydı oluşturma görünümü
    """
    template_name = 'core/patient_registration.html'
    form_class = PatientRegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Hasta kaydı başarıyla oluşturuldu.'))
        return response

# Randevu Görünümleri
class AppointmentListView(LoginRequiredMixin, ListView):
    """
    Randevu listesi görünümü
    """
    model = Appointment
    template_name = 'core/appointment_list.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filtreleme
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if user.is_patient():
            queryset = queryset.filter(patient=user)
        elif user.is_doctor():
            queryset = queryset.filter(doctor=user)
        
        if status:
            queryset = queryset.filter(status=status)
            
        if search:
            if user.is_patient():
                queryset = queryset.filter(
                    Q(doctor__first_name__icontains=search) |
                    Q(doctor__last_name__icontains=search) |
                    Q(description__icontains=search)
                )
            elif user.is_doctor() or user.is_receptionist() or user.is_admin_user():
                queryset = queryset.filter(
                    Q(patient__first_name__icontains=search) |
                    Q(patient__last_name__icontains=search) |
                    Q(description__icontains=search)
                )
        
        return queryset.order_by('-date', '-time')

class AppointmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Randevu oluşturma görünümü
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'core/appointment_form.html'
    success_url = reverse_lazy('appointment-list')
    
    def test_func(self):
        # Tüm kullanıcılar randevu oluşturabilir
        return True
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        # URL'den doktor ID'si alınırsa doktoru otomatik seç
        doctor_id = self.request.GET.get('doctor')
        if doctor_id:
            initial['doctor'] = doctor_id
        
        # URL'den hasta ID'si alınırsa hastayı otomatik seç
        patient_id = self.request.GET.get('patient')
        if patient_id:
            initial['patient'] = patient_id
        elif self.request.user.is_patient():
            initial['patient'] = self.request.user.id
            
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Randevu başarıyla oluşturuldu.'))
        return response

class AppointmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Randevu güncelleme görünümü
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'core/appointment_form.html'
    success_url = reverse_lazy('appointment-list')
    
    def test_func(self):
        appointment = self.get_object()
        user = self.request.user
        # Doktorlar ve resepsiyonistler kendi randevularını güncelleyebilir
        if user.is_doctor():
            return appointment.doctor == user
        return user.is_receptionist() or user.is_admin_user()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Randevu başarıyla güncellendi.'))
        return response

class AppointmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Randevu detay görünümü
    """
    model = Appointment
    template_name = 'core/appointment_detail.html'
    context_object_name = 'appointment'
    
    def test_func(self):
        appointment = self.get_object()
        user = self.request.user
        # Doktor ve hasta sadece kendi randevularını görebilir
        if user.is_patient():
            return appointment.patient == user
        elif user.is_doctor():
            return appointment.doctor == user
        return user.is_receptionist() or user.is_admin_user()

class AppointmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Randevu silme görünümü
    """
    model = Appointment
    template_name = 'core/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointment-list')
    
    def test_func(self):
        # Sadece resepsiyonistler ve adminler randevu silebilir
        return self.request.user.is_receptionist() or self.request.user.is_admin_user()
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, _('Randevu başarıyla silindi.'))
        return response

# Tedavi Görünümleri
class TreatmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Tedavi oluşturma görünümü
    """
    model = Treatment
    form_class = TreatmentForm
    template_name = 'core/treatment_form.html'
    success_url = reverse_lazy('appointment-list')
    
    def test_func(self):
        # Sadece doktorlar tedavi oluşturabilir
        return self.request.user.is_doctor()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['prescription_formset'] = PrescriptionFormSet(self.request.POST)
        else:
            context['prescription_formset'] = PrescriptionFormSet()
        
        # Randevu bilgilerini ekle
        appointment_id = self.kwargs.get('appointment_id')
        if appointment_id:
            context['appointment'] = get_object_or_404(Appointment, id=appointment_id)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        prescription_formset = context['prescription_formset']
        
        # Randevu ile ilişkilendir
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Doktor sadece kendi randevularına tedavi ekleyebilir
        if appointment.doctor != self.request.user:
            messages.error(self.request, _('Bu randevu için tedavi ekleyemezsiniz.'))
            return redirect('appointment-list')
        
        # Randevu durumunu tamamlandı olarak işaretle
        appointment.status = 'completed'
        appointment.save()
        
        # Tedavi ve reçeteleri kaydet
        if prescription_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.appointment = appointment
            self.object.save()
            
            prescription_formset.instance = self.object
            prescription_formset.save()
            
            messages.success(self.request, _('Tedavi ve reçeteler başarıyla kaydedildi.'))
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class TreatmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Tedavi güncelleme görünümü
    """
    model = Treatment
    form_class = TreatmentForm
    template_name = 'core/treatment_form.html'
    success_url = reverse_lazy('appointment-list')
    
    def test_func(self):
        treatment = self.get_object()
        # Sadece tedaviyi oluşturan doktor güncelleyebilir
        return self.request.user.is_doctor() and treatment.appointment.doctor == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['prescription_formset'] = PrescriptionFormSet(self.request.POST, instance=self.object)
        else:
            context['prescription_formset'] = PrescriptionFormSet(instance=self.object)
        
        context['appointment'] = self.object.appointment
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        prescription_formset = context['prescription_formset']
        
        if prescription_formset.is_valid():
            self.object = form.save()
            prescription_formset.instance = self.object
            prescription_formset.save()
            
            messages.success(self.request, _('Tedavi ve reçeteler başarıyla güncellendi.'))
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class TreatmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Tedavi detay görünümü
    """
    model = Treatment
    template_name = 'core/treatment_detail.html'
    context_object_name = 'treatment'
    
    def test_func(self):
        treatment = self.get_object()
        user = self.request.user
        # Hasta ve doktor sadece kendi tedavilerini görebilir
        if user.is_patient():
            return treatment.appointment.patient == user
        elif user.is_doctor():
            return treatment.appointment.doctor == user
        return user.is_receptionist() or user.is_admin_user()

# Hasta Görünümleri
class PatientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Hasta listesi görünümü
    """
    model = User
    template_name = 'core/patient_list.html'
    context_object_name = 'patients'
    
    def test_func(self):
        # Sadece doktorlar, resepsiyonistler ve adminler hasta listesini görebilir
        user = self.request.user
        return user.is_doctor() or user.is_receptionist() or user.is_admin_user()
    
    def get_queryset(self):
        queryset = User.objects.filter(user_type='patient')
        
        # Doktorlar sadece kendilerine randevu alan hastaları görebilir
        if self.request.user.is_doctor():
            doctor = self.request.user
            patient_ids = Appointment.objects.filter(doctor=doctor).values_list('patient_id', flat=True)
            queryset = queryset.filter(id__in=patient_ids).distinct()
        
        # Arama
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('first_name', 'last_name')

class PatientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Hasta detay görünümü
    """
    model = User
    template_name = 'core/patient_detail.html'
    context_object_name = 'patient'
    
    def test_func(self):
        patient = self.get_object()
        user = self.request.user
        
        # Hastalar sadece kendi profillerini görebilir
        if user.is_patient():
            return patient == user
        
        # Doktorlar sadece kendilerine randevu alan hastaları görebilir
        if user.is_doctor():
            return Appointment.objects.filter(doctor=user, patient=patient).exists()
            
        # Resepsiyonistler ve adminler tüm hastaları görebilir
        return user.is_receptionist() or user.is_admin_user()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        
        # Hasta randevuları
        appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
        
        # Hasta tedavileri
        treatments = Treatment.objects.filter(appointment__patient=patient).order_by('-created_at')
        
        context.update({
            'appointments': appointments,
            'treatments': treatments
        })
        
        return context

# Doktor Görünümleri
class DoctorListView(LoginRequiredMixin, ListView):
    """
    Doktor listesi görünümü
    """
    model = User
    template_name = 'core/doctor_list.html'
    context_object_name = 'doctors'
    
    def get_queryset(self):
        queryset = User.objects.filter(user_type='doctor')
        
        # Arama
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(specialization__icontains=search)
            )
        
        return queryset.order_by('first_name', 'last_name')

class DoctorCreationView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Doktor oluşturma görünümü
    """
    model = User
    form_class = DoctorCreationForm
    template_name = 'core/doctor_form.html'
    success_url = reverse_lazy('doctor-list')
    
    def test_func(self):
        # Sadece admin kullanıcılar doktor ekleyebilir
        return self.request.user.is_admin_user() or self.request.user.is_superuser
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Doktor hesabı başarıyla oluşturuldu.'))
        return response

class DoctorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Doktor güncelleme görünümü
    """
    model = User
    form_class = DoctorUpdateForm
    template_name = 'core/doctor_form.html'
    success_url = reverse_lazy('doctor-list')
    
    def test_func(self):
        # Sadece admin kullanıcılar doktor bilgilerini güncelleyebilir
        return self.request.user.is_admin_user() or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Doktor bilgileri başarıyla güncellendi.'))
        return response
