from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

from .models_lab import LabTest, TestResult
from .forms import LabTestForm, TestResultForm
from treatments.models import Treatment

User = settings.AUTH_USER_MODEL

class LabTestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Laboratuvar testleri listesi görünümü.
    """
    model = LabTest
    template_name = 'treatments/lab_test_list.html'
    context_object_name = 'lab_tests'
    
    def test_func(self):
        # Sadece doktorlar, laborantlar ve adminler görebilir
        # Hastalar sadece kendi testlerini görebilir
        user = self.request.user
        patient_id = self.kwargs.get('patient_id')
        
        if user.is_patient():
            return str(user.id) == str(patient_id)
        return user.is_doctor() or user.is_receptionist() or user.is_admin_user()
    
    def get_queryset(self):
        user = self.request.user
        patient_id = self.kwargs.get('patient_id')
        
        if patient_id:
            return LabTest.objects.filter(patient_id=patient_id).order_by('-requested_date')
        elif user.is_doctor():
            return LabTest.objects.filter(doctor=user).order_by('-requested_date')
        else:
            return LabTest.objects.all().order_by('-requested_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(User, id=patient_id)
        return context

class LabTestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Laboratuvar testi detay görünümü.
    """
    model = LabTest
    template_name = 'treatments/lab_test_detail.html'
    context_object_name = 'lab_test'
    
    def test_func(self):
        lab_test = self.get_object()
        user = self.request.user
        
        if user.is_patient():
            return lab_test.patient == user
        return user.is_doctor() or user.is_receptionist() or user.is_admin_user()

class LabTestCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Laboratuvar testi oluşturma görünümü.
    """
    model = LabTest
    form_class = LabTestForm
    template_name = 'treatments/lab_test_form.html'
    
    def test_func(self):
        # Sadece doktorlar, adminler ve resepsiyonistler ekleyebilir
        user = self.request.user
        return user.is_doctor() or user.is_admin_user() or user.is_receptionist()
    
    def get_initial(self):
        initial = super().get_initial()
        treatment_id = self.kwargs.get('treatment_id')
        doctor_id = self.request.user.id if self.request.user.is_doctor() else None
        
        if treatment_id:
            treatment = get_object_or_404(Treatment, id=treatment_id)
            initial['treatment'] = treatment
            initial['patient'] = treatment.appointment.patient.id
            initial['doctor'] = treatment.appointment.doctor.id
        elif doctor_id:
            initial['doctor'] = doctor_id
            
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
            
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        treatment_id = self.kwargs.get('treatment_id')
        patient_id = self.kwargs.get('patient_id')
        
        if treatment_id:
            context['treatment'] = get_object_or_404(Treatment, id=treatment_id)
        if patient_id:
            context['patient'] = get_object_or_404(User, id=patient_id)
            
        context['title'] = _('Yeni Laboratuvar Testi İste')
        return context
    
    def get_success_url(self):
        if 'treatment_id' in self.kwargs:
            return reverse_lazy('treatment-detail', kwargs={'pk': self.kwargs['treatment_id']})
        elif 'patient_id' in self.kwargs:
            return reverse_lazy('lab-test-list', kwargs={'patient_id': self.kwargs['patient_id']})
        return reverse_lazy('lab-test-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Laboratuvar testi başarıyla oluşturuldu.'))
        return response

class LabTestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Laboratuvar testi güncelleme görünümü.
    """
    model = LabTest
    form_class = LabTestForm
    template_name = 'treatments/lab_test_form.html'
    
    def test_func(self):
        lab_test = self.get_object()
        user = self.request.user
        # Sadece isteyen doktor veya adminler güncelleyebilir
        if user.is_doctor():
            return lab_test.doctor == user
        return user.is_admin_user()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Laboratuvar Testi Güncelle')
        return context
    
    def get_success_url(self):
        return reverse_lazy('lab-test-detail', kwargs={'pk': self.object.id})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Laboratuvar testi başarıyla güncellendi.'))
        return response

class LabTestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Laboratuvar testi silme görünümü.
    """
    model = LabTest
    template_name = 'treatments/lab_test_confirm_delete.html'
    
    def test_func(self):
        lab_test = self.get_object()
        user = self.request.user
        # Sadece isteyen doktor veya adminler silebilir
        if user.is_doctor():
            return lab_test.doctor == user
        return user.is_admin_user()
    
    def get_success_url(self):
        if hasattr(self.object, 'patient'):
            return reverse_lazy('lab-test-list', kwargs={'patient_id': self.object.patient.id})
        return reverse_lazy('lab-test-list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, _('Laboratuvar testi başarıyla silindi.'))
        return response

class TestResultCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Test sonucu oluşturma görünümü.
    """
    model = TestResult
    form_class = TestResultForm
    template_name = 'treatments/test_result_form.html'
    
    def test_func(self):
        # Sadece doktorlar, laborantlar ve adminler ekleyebilir
        user = self.request.user
        return user.is_doctor() or user.is_admin_user() or user.is_receptionist()
    
    def get_initial(self):
        initial = super().get_initial()
        lab_test_id = self.kwargs.get('lab_test_id')
        
        if lab_test_id:
            lab_test = get_object_or_404(LabTest, id=lab_test_id)
            initial['lab_test'] = lab_test
            
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lab_test_id = self.kwargs.get('lab_test_id')
        
        if lab_test_id:
            context['lab_test'] = get_object_or_404(LabTest, id=lab_test_id)
            
        context['title'] = _('Test Sonucu Ekle')
        return context
    
    def get_success_url(self):
        return reverse_lazy('lab-test-detail', kwargs={'pk': self.object.lab_test.id})
    
    def form_valid(self, form):
        form.instance.lab_test.status = 'completed'
        form.instance.lab_test.completed_date = timezone.now()
        form.instance.lab_test.save()
        
        response = super().form_valid(form)
        messages.success(self.request, _('Test sonucu başarıyla eklendi.'))
        return response

class TestResultUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Test sonucu güncelleme görünümü.
    """
    model = TestResult
    form_class = TestResultForm
    template_name = 'treatments/test_result_form.html'
    
    def test_func(self):
        # Sadece doktorlar, laborantlar ve adminler güncelleyebilir
        user = self.request.user
        return user.is_doctor() or user.is_admin_user() or user.is_receptionist()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Test Sonucu Güncelle')
        context['lab_test'] = self.object.lab_test
        return context
    
    def get_success_url(self):
        return reverse_lazy('lab-test-detail', kwargs={'pk': self.object.lab_test.id})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Test sonucu başarıyla güncellendi.'))
        return response
