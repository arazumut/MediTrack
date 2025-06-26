from django import forms
from django.contrib.auth import get_user_model
from .models import TeleconsultationSession, TeleconsultationMessage, TeleconsultationSettings

User = get_user_model()


class TeleconsultationSessionForm(forms.ModelForm):
    class Meta:
        model = TeleconsultationSession
        fields = ['patient', 'doctor', 'scheduled_time', 'duration_minutes', 'session_type', 'notes']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'max': '120'}),
            'session_type': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = User.objects.filter(user_type='patient')
        self.fields['doctor'].queryset = User.objects.filter(user_type='doctor')


class TeleconsultationMessageForm(forms.ModelForm):
    class Meta:
        model = TeleconsultationMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Type your message...'
            })
        }


class TeleconsultationSettingsForm(forms.ModelForm):
    class Meta:
        model = TeleconsultationSettings
        fields = [
            'enable_video', 'enable_audio', 'enable_screen_share',
            'enable_chat', 'enable_file_sharing', 'auto_record',
            'notification_sound', 'camera_device', 'microphone_device'
        ]
        widgets = {
            'enable_video': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_audio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_screen_share': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_chat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_file_sharing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_record': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notification_sound': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'camera_device': forms.TextInput(attrs={'class': 'form-control'}),
            'microphone_device': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SessionSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search sessions...'
        })
    )
    status_filter = forms.ChoiceField(
        choices=[('', 'All Status')] + TeleconsultationSession.STATUS_CHOICES,
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
