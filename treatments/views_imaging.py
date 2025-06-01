from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import FileResponse
from django.utils import timezone


from .models_imaging import MedicalImage, Report
from .forms_imaging import (
    MedicalImageForm, 
    ReportForm, 
    MedicalImageSearchForm, 
    ReportSearchForm
)
from .models import Treatment

# Medical Image views
class MedicalImageListView(LoginRequiredMixin, ListView):
    """
    Display a list of medical images
    """
    model = MedicalImage
    template_name = 'treatments/medical_image_list.html'
    context_object_name = 'medical_images'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by patient if specified
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by treatment if specified
        treatment_id = self.kwargs.get('treatment_id')
        if treatment_id:
            queryset = queryset.filter(treatment_id=treatment_id)
            
        # Apply search filters
        form = MedicalImageSearchForm(self.request.GET)
        if form.is_valid():
            image_type = form.cleaned_data.get('image_type')
            body_part = form.cleaned_data.get('body_part')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            
            if image_type:
                queryset = queryset.filter(image_type=image_type)
            
            if body_part:
                queryset = queryset.filter(body_part__icontains=body_part)
            
            if date_from:
                queryset = queryset.filter(taken_date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(taken_date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MedicalImageSearchForm(self.request.GET)
        
        # Add patient context if filtering by patient
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            context['patient'] = get_object_or_404(User, id=patient_id, user_type='patient')
        
        # Add treatment context if filtering by treatment
        treatment_id = self.kwargs.get('treatment_id')
        if treatment_id:
            context['treatment'] = get_object_or_404(Treatment, id=treatment_id)
            
        return context

class MedicalImageDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information about a medical image
    """
    model = MedicalImage
    template_name = 'treatments/medical_image_detail.html'
    context_object_name = 'medical_image'

class MedicalImageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Create a new medical image record
    """
    model = MedicalImage
    form_class = MedicalImageForm
    template_name = 'treatments/medical_image_form.html'
    permission_required = 'treatments.add_medicalimage'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['treatment_id'] = self.kwargs.get('treatment_id')
        kwargs['patient_id'] = self.kwargs.get('patient_id')
        kwargs['doctor'] = self.request.user if self.request.user.user_type == 'doctor' else None
        return kwargs
    
    def get_success_url(self):
        if 'treatment_id' in self.kwargs:
            return reverse('treatment-detail', kwargs={'pk': self.kwargs['treatment_id']})
        elif 'patient_id' in self.kwargs:
            return reverse('medical-image-list', kwargs={'patient_id': self.kwargs['patient_id']})
        return reverse('medical-image-list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Tıbbi görüntü başarıyla eklendi."))
        return super().form_valid(form)

class MedicalImageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Update an existing medical image record
    """
    model = MedicalImage
    form_class = MedicalImageForm
    template_name = 'treatments/medical_image_form.html'
    permission_required = 'treatments.change_medicalimage'
    
    def get_success_url(self):
        return reverse('medical-image-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _("Tıbbi görüntü başarıyla güncellendi."))
        return super().form_valid(form)

class MedicalImageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete a medical image record
    """
    model = MedicalImage
    template_name = 'treatments/medical_image_confirm_delete.html'
    permission_required = 'treatments.delete_medicalimage'
    
    def get_success_url(self):
        if self.object.treatment:
            return reverse('treatment-detail', kwargs={'pk': self.object.treatment.pk})
        return reverse('medical-image-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Tıbbi görüntü başarıyla silindi."))
        return super().delete(request, *args, **kwargs)

# Report views
class ReportListView(LoginRequiredMixin, ListView):
    """
    Display a list of medical reports
    """
    model = Report
    template_name = 'treatments/report_list.html'
    context_object_name = 'reports'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by patient if specified
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by treatment if specified
        treatment_id = self.kwargs.get('treatment_id')
        if treatment_id:
            queryset = queryset.filter(treatment_id=treatment_id)
            
        # Apply search filters
        form = ReportSearchForm(self.request.GET)
        if form.is_valid():
            report_type = form.cleaned_data.get('report_type')
            title = form.cleaned_data.get('title')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            
            if report_type:
                queryset = queryset.filter(report_type=report_type)
            
            if title:
                queryset = queryset.filter(title__icontains=title)
            
            if date_from:
                queryset = queryset.filter(valid_from__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(valid_from__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ReportSearchForm(self.request.GET)
        
        # Add patient context if filtering by patient
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            context['patient'] = get_object_or_404(User, id=patient_id, user_type='patient')
        
        # Add treatment context if filtering by treatment
        treatment_id = self.kwargs.get('treatment_id')
        if treatment_id:
            context['treatment'] = get_object_or_404(Treatment, id=treatment_id)
            
        return context

class ReportDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information about a medical report
    """
    model = Report
    template_name = 'treatments/report_detail.html'
    context_object_name = 'report'

class ReportCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Create a new medical report
    """
    model = Report
    form_class = ReportForm
    template_name = 'treatments/report_form.html'
    permission_required = 'treatments.add_report'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['treatment_id'] = self.kwargs.get('treatment_id')
        kwargs['patient_id'] = self.kwargs.get('patient_id')
        kwargs['doctor'] = self.request.user if self.request.user.user_type == 'doctor' else None
        return kwargs
    
    def get_success_url(self):
        if 'treatment_id' in self.kwargs:
            return reverse('treatment-detail', kwargs={'pk': self.kwargs['treatment_id']})
        elif 'patient_id' in self.kwargs:
            return reverse('report-list', kwargs={'patient_id': self.kwargs['patient_id']})
        return reverse('report-list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Tıbbi rapor başarıyla oluşturuldu."))
        return super().form_valid(form)

class ReportUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Update an existing medical report
    """
    model = Report
    form_class = ReportForm
    template_name = 'treatments/report_form.html'
    permission_required = 'treatments.change_report'
    
    def get_success_url(self):
        return reverse('report-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _("Tıbbi rapor başarıyla güncellendi."))
        return super().form_valid(form)

class ReportDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete a medical report
    """
    model = Report
    template_name = 'treatments/report_confirm_delete.html'
    permission_required = 'treatments.delete_report'
    
    def get_success_url(self):
        if self.object.treatment:
            return reverse('treatment-detail', kwargs={'pk': self.object.treatment.pk})
        return reverse('report-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Tıbbi rapor başarıyla silindi."))
        return super().delete(request, *args, **kwargs)

# File serving views
@login_required
def serve_medical_image(request, pk):
    """
    Serve the medical image file
    """
    medical_image = get_object_or_404(MedicalImage, pk=pk)
    
    # Check permissions
    if not (request.user.is_staff or request.user == medical_image.patient or 
            request.user == medical_image.doctor):
        messages.error(request, _("Bu görüntüyü görüntüleme yetkiniz yok."))
        return redirect('medical-image-detail', pk=pk)
    
    try:
        return FileResponse(medical_image.image_file.open(), content_type='image/jpeg')
    except Exception as e:
        messages.error(request, _("Dosya açılırken bir hata oluştu: {}").format(str(e)))
        return redirect('medical-image-detail', pk=pk)

@login_required
def serve_report_file(request, pk):
    """
    Serve the report file
    """
    report = get_object_or_404(Report, pk=pk)
    
    # Check permissions
    if not (request.user.is_staff or request.user == report.patient or 
            request.user == report.doctor):
        messages.error(request, _("Bu raporu görüntüleme yetkiniz yok."))
        return redirect('report-detail', pk=pk)
    
    if not report.report_file:
        messages.error(request, _("Bu rapor için dosya yüklenmemiş."))
        return redirect('report-detail', pk=pk)
    
    try:
        return FileResponse(report.report_file.open(), content_type='application/pdf')
    except Exception as e:
        messages.error(request, _("Dosya açılırken bir hata oluştu: {}").format(str(e)))
        return redirect('report-detail', pk=pk)
