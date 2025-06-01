from django import forms
from django.utils.translation import gettext_lazy as _
from .models_imaging import MedicalImage, Report
from django.utils import timezone

class MedicalImageForm(forms.ModelForm):
    """
    Form for creating and updating medical image records
    """
    class Meta:
        model = MedicalImage
        fields = ['treatment', 'patient', 'doctor', 'image_type', 'body_part', 
                  'image_file', 'description', 'taken_date']
        widgets = {
            'treatment': forms.Select(attrs={'class': 'form-select'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'image_type': forms.Select(attrs={'class': 'form-select'}),
            'body_part': forms.TextInput(attrs={'class': 'form-control'}),
            'image_file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'taken_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        treatment_id = kwargs.pop('treatment_id', None)
        patient_id = kwargs.pop('patient_id', None)
        doctor = kwargs.pop('doctor', None)
        
        super().__init__(*args, **kwargs)
        
        if treatment_id:
            self.fields['treatment'].initial = treatment_id
            self.fields['treatment'].widget.attrs['readonly'] = True
            # Hide treatment field if it's pre-selected
            self.fields['treatment'].widget = forms.HiddenInput()
            
            # Pre-fill patient from treatment
            from treatments.models import Treatment
            try:
                treatment = Treatment.objects.get(id=treatment_id)
                self.fields['patient'].initial = treatment.appointment.patient.id
                self.fields['patient'].widget.attrs['readonly'] = True
                self.fields['patient'].widget = forms.HiddenInput()
            except Treatment.DoesNotExist:
                pass
        
        if patient_id:
            self.fields['patient'].initial = patient_id
            self.fields['patient'].widget.attrs['readonly'] = True
            # Hide patient field if it's pre-selected
            self.fields['patient'].widget = forms.HiddenInput()
        
        if doctor:
            self.fields['doctor'].initial = doctor.id
            self.fields['doctor'].widget.attrs['readonly'] = True
            # Hide doctor field if it's the current user
            self.fields['doctor'].widget = forms.HiddenInput()
        
        # Set default taken_date to today
        self.fields['taken_date'].initial = timezone.now().date()

class ReportForm(forms.ModelForm):
    """
    Form for creating and updating medical reports
    """
    class Meta:
        model = Report
        fields = ['treatment', 'patient', 'doctor', 'report_type', 'title', 
                 'content', 'valid_from', 'valid_until', 'report_file']
        widgets = {
            'treatment': forms.Select(attrs={'class': 'form-select'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'report_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        treatment_id = kwargs.pop('treatment_id', None)
        patient_id = kwargs.pop('patient_id', None)
        doctor = kwargs.pop('doctor', None)
        
        super().__init__(*args, **kwargs)
        
        if treatment_id:
            self.fields['treatment'].initial = treatment_id
            self.fields['treatment'].widget.attrs['readonly'] = True
            # Hide treatment field if it's pre-selected
            self.fields['treatment'].widget = forms.HiddenInput()
            
            # Pre-fill patient from treatment
            from treatments.models import Treatment
            try:
                treatment = Treatment.objects.get(id=treatment_id)
                self.fields['patient'].initial = treatment.appointment.patient.id
                self.fields['patient'].widget.attrs['readonly'] = True
                self.fields['patient'].widget = forms.HiddenInput()
            except Treatment.DoesNotExist:
                pass
        
        if patient_id:
            self.fields['patient'].initial = patient_id
            self.fields['patient'].widget.attrs['readonly'] = True
            # Hide patient field if it's pre-selected
            self.fields['patient'].widget = forms.HiddenInput()
        
        if doctor:
            self.fields['doctor'].initial = doctor.id
            self.fields['doctor'].widget.attrs['readonly'] = True
            # Hide doctor field if it's the current user
            self.fields['doctor'].widget = forms.HiddenInput()
        
        # Set default valid_from to today
        self.fields['valid_from'].initial = timezone.now().date()

class MedicalImageSearchForm(forms.Form):
    """
    Form for searching medical images
    """
    image_type = forms.ChoiceField(
        label=_('Görüntü Tipi'),
        required=False,
        choices=[('', _('Tümü'))] + MedicalImage.IMAGE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    body_part = forms.CharField(
        label=_('Vücut Bölgesi'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Vücut bölgesi ara...')})
    )
    date_from = forms.DateField(
        label=_('Başlangıç Tarihi'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        label=_('Bitiş Tarihi'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

class ReportSearchForm(forms.Form):
    """
    Form for searching medical reports
    """
    report_type = forms.ChoiceField(
        label=_('Rapor Tipi'),
        required=False,
        choices=[('', _('Tümü'))] + Report.REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    title = forms.CharField(
        label=_('Başlık'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Rapor başlığı ara...')})
    )
    date_from = forms.DateField(
        label=_('Başlangıç Tarihi'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        label=_('Bitiş Tarihi'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
