from django import forms
from django.utils.translation import gettext_lazy as _
from .models_medications import Medication, MedicationInteraction
from .models import Prescription

class MedicationForm(forms.ModelForm):
    """
    Form for creating and updating medication entries in the database
    """
    class Meta:
        model = Medication
        fields = ['name', 'active_ingredient', 'drug_code', 'description', 
                 'side_effects', 'contraindications', 'is_prescription']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'active_ingredient': forms.TextInput(attrs={'class': 'form-control'}),
            'drug_code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'side_effects': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contraindications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_prescription': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MedicationInteractionForm(forms.ModelForm):
    """
    Form for creating and updating medication interaction entries
    """
    class Meta:
        model = MedicationInteraction
        fields = ['medication1', 'medication2', 'description', 'severity', 'recommendations']
        widgets = {
            'medication1': forms.Select(attrs={'class': 'form-select'}),
            'medication2': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        medication1 = cleaned_data.get('medication1')
        medication2 = cleaned_data.get('medication2')
        
        if medication1 and medication2 and medication1 == medication2:
            raise forms.ValidationError(_("Bir ilaç kendisiyle etkileşim içinde olamaz."))
            
        return cleaned_data

class PrescriptionMedicationForm(forms.ModelForm):
    """
    Extended Prescription form that includes medication selection from the database
    """
    medication = forms.ModelChoiceField(
        queryset=Medication.objects.all(),
        label=_('İlaç Seçimi'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Prescription
        fields = ['name', 'dosage', 'instructions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False  # Not required if medication is selected
        
    def clean(self):
        cleaned_data = super().clean()
        medication = cleaned_data.get('medication')
        name = cleaned_data.get('name')
        
        if not medication and not name:
            raise forms.ValidationError(_("İlaç seçimi yapmalı veya ilaç adı girmelisiniz."))
            
        # If medication is selected, populate name field
        if medication and not name:
            cleaned_data['name'] = medication.name
            
        return cleaned_data

class MedicationSearchForm(forms.Form):
    """
    Form for searching medications in the database
    """
    search_query = forms.CharField(
        label=_('Arama'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('İlaç adı, etken madde veya açıklama')})
    )
    is_prescription = forms.ChoiceField(
        label=_('Reçete Durumu'),
        required=False,
        choices=[('', _('Hepsi')), ('True', _('Reçeteli')), ('False', _('Reçetesiz'))],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
