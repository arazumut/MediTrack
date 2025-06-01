from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models_medications import Medication, MedicationInteraction
from .forms_medications import (
    MedicationForm, 
    MedicationInteractionForm, 
    MedicationSearchForm, 
    PrescriptionMedicationForm
)

# Medication views
class MedicationListView(LoginRequiredMixin, ListView):
    """
    Display a list of all medications in the system.
    """
    model = Medication
    template_name = 'treatments/medication_list.html'
    context_object_name = 'medications'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = MedicationSearchForm(self.request.GET)
        
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            is_prescription = form.cleaned_data.get('is_prescription')
            
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) | 
                    Q(active_ingredient__icontains=search_query) | 
                    Q(description__icontains=search_query)
                )
            
            if is_prescription:
                queryset = queryset.filter(is_prescription=(is_prescription == 'True'))
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MedicationSearchForm(self.request.GET)
        return context

class MedicationDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information about a medication.
    """
    model = Medication
    template_name = 'treatments/medication_detail.html'
    context_object_name = 'medication'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medication = self.get_object()
        
        # Get all interactions for this medication
        interactions = MedicationInteraction.objects.filter(
            Q(medication1=medication) | Q(medication2=medication)
        )
        
        context['interactions'] = interactions
        return context

class MedicationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Create a new medication entry.
    """
    model = Medication
    form_class = MedicationForm
    template_name = 'treatments/medication_form.html'
    success_url = reverse_lazy('medication_list')
    permission_required = 'treatments.add_medication'
    
    def form_valid(self, form):
        messages.success(self.request, _("İlaç başarıyla eklendi."))
        return super().form_valid(form)

class MedicationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Update an existing medication entry.
    """
    model = Medication
    form_class = MedicationForm
    template_name = 'treatments/medication_form.html'
    permission_required = 'treatments.change_medication'
    
    def get_success_url(self):
        return reverse('medication_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _("İlaç bilgileri başarıyla güncellendi."))
        return super().form_valid(form)

class MedicationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete a medication entry.
    """
    model = Medication
    template_name = 'treatments/medication_confirm_delete.html'
    success_url = reverse_lazy('medication_list')
    permission_required = 'treatments.delete_medication'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("İlaç başarıyla silindi."))
        return super().delete(request, *args, **kwargs)

# Medication Interaction views
class InteractionListView(LoginRequiredMixin, ListView):
    """
    Display a list of all medication interactions.
    """
    model = MedicationInteraction
    template_name = 'treatments/interaction_list.html'
    context_object_name = 'interactions'
    paginate_by = 10

class InteractionDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information about a medication interaction.
    """
    model = MedicationInteraction
    template_name = 'treatments/interaction_detail.html'
    context_object_name = 'interaction'

class InteractionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Create a new medication interaction entry.
    """
    model = MedicationInteraction
    form_class = MedicationInteractionForm
    template_name = 'treatments/interaction_form.html'
    success_url = reverse_lazy('interaction_list')
    permission_required = 'treatments.add_medicationinteraction'
    
    def form_valid(self, form):
        messages.success(self.request, _("İlaç etkileşimi başarıyla eklendi."))
        return super().form_valid(form)

class InteractionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Update an existing medication interaction entry.
    """
    model = MedicationInteraction
    form_class = MedicationInteractionForm
    template_name = 'treatments/interaction_form.html'
    permission_required = 'treatments.change_medicationinteraction'
    
    def get_success_url(self):
        return reverse('interaction_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _("İlaç etkileşimi başarıyla güncellendi."))
        return super().form_valid(form)

class InteractionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete a medication interaction entry.
    """
    model = MedicationInteraction
    template_name = 'treatments/interaction_confirm_delete.html'
    success_url = reverse_lazy('interaction_list')
    permission_required = 'treatments.delete_medicationinteraction'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("İlaç etkileşimi başarıyla silindi."))
        return super().delete(request, *args, **kwargs)

# Patient medication views and utilities
@login_required
def patient_medications(request, patient_id):
    """
    View medications prescribed to a specific patient.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    patient = get_object_or_404(User, pk=patient_id, user_type='patient')
    
    # Get all prescriptions for this patient from all treatments
    from .models import Prescription
    prescriptions = Prescription.objects.filter(
        treatment__appointment__patient=patient
    ).order_by('-created_at')
    
    paginator = Paginator(prescriptions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'treatments/patient_medications.html', {
        'patient': patient,
        'page_obj': page_obj,
    })

@login_required
def medication_search_api(request):
    """
    API endpoint for searching medications (used by AJAX).
    """
    search_term = request.GET.get('term', '')
    
    if not search_term:
        return JsonResponse({'results': []})
    
    medications = Medication.objects.filter(
        Q(name__icontains=search_term) | 
        Q(active_ingredient__icontains=search_term)
    )[:10]
    
    results = [{
        'id': med.id,
        'text': f"{med.name} ({med.active_ingredient})",
        'name': med.name,
        'active_ingredient': med.active_ingredient,
        'is_prescription': med.is_prescription,
    } for med in medications]
    
    return JsonResponse({'results': results})

# Import in treatments/urls.py
from .views_medications import (
    MedicationListView, MedicationDetailView, MedicationCreateView, 
    MedicationUpdateView, MedicationDeleteView,
    InteractionListView, InteractionDetailView, InteractionCreateView,
    InteractionUpdateView, InteractionDeleteView,
    patient_medications, medication_search_api
)
