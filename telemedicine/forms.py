from django import forms
from django.contrib.auth import get_user_model
from .models import TelemedicineAppointment, TeleMedicineMessage, TeleMedicineSettings, TelemedDocument, TelemedPrescription, TelemedNote

User = get_user_model()


class TelemedicineAppointmentForm(forms.ModelForm):
    class Meta:
        model = TelemedicineAppointment
        fields = ['patient', 'doctor', 'date', 'time', 'duration', 'description', 'chief_complaint']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'max': '120'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = User.objects.filter(user_type='patient')
        self.fields['doctor'].queryset = User.objects.filter(user_type='doctor')


class TeleMedicineMessageForm(forms.ModelForm):
    class Meta:
        model = TeleMedicineMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Mesajınızı yazın...'
            })
        }


class TeleMedicineSettingsForm(forms.ModelForm):
    class Meta:
        model = TeleMedicineSettings
        fields = [
            'default_camera_enabled', 'default_microphone_enabled', 'video_quality',
            'consultation_reminders', 'reminder_minutes_before', 'email_notifications',
            'sms_notifications', 'require_waiting_room', 'allow_recording',
            'allow_file_sharing', 'max_consultation_duration', 'auto_end_consultation'
        ]
        widgets = {
            'default_camera_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'default_microphone_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'video_quality': forms.Select(attrs={'class': 'form-control'}),
            'consultation_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reminder_minutes_before': forms.NumberInput(attrs={'class': 'form-control', 'min': '5', 'max': '60'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'require_waiting_room': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_recording': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_file_sharing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_consultation_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'max': '180'}),
            'auto_end_consultation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AppointmentSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Randevuları ara...'
        })
    )
    status_filter = forms.ChoiceField(
        choices=[('', 'Tüm Durumlar')] + list(TelemedicineAppointment.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class TelemedDocumentForm(forms.ModelForm):
    class Meta:
        model = TelemedDocument
        fields = ['title', 'document_type', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TelemedPrescriptionForm(forms.ModelForm):
    class Meta:
        model = TelemedPrescription
        fields = ['medications', 'instructions', 'duration_days', 'is_renewable']
        widgets = {
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '90'}),
            'is_renewable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TelemedNoteForm(forms.ModelForm):
    class Meta:
        model = TelemedNote
        fields = ['title', 'content', 'note_type', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'note_type': forms.Select(attrs={'class': 'form-control'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
