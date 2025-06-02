from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import datetime

from appointments.models import Appointment
from treatments.models import Treatment, Prescription
from treatments.models_medications import Medication, MedicationInteraction
from treatments.models_medical_history import MedicalHistory

User = get_user_model()

class LoginForm(AuthenticationForm):
    """
    Kullanıcı giriş formu, AuthenticationForm'u özelleştirir.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Kullanıcı Adı')}),
        label=_('Kullanıcı Adı')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Şifre')}),
        label=_('Şifre')
    )

class PatientRegistrationForm(UserCreationForm):
    """
    Hasta kayıt formu, yeni bir hasta kullanıcı oluşturmak için kullanılır.
    """
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ad')}),
        label=_('Ad')
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Soyad')}),
        label=_('Soyad')
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('E-posta')}),
        label=_('E-posta')
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Doğum Tarihi')
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Telefon Numarası')}),
        label=_('Telefon Numarası')
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Adres')}),
        label=_('Adres')
    )
    blood_type = forms.ChoiceField(
        choices=[
            ('', _('Seçiniz')),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('0+', '0+'),
            ('0-', '0-'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Kan Grubu')
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 
                 'date_of_birth', 'phone_number', 'address', 'blood_type')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Kullanıcı Adı')})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Şifre')})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Şifre (Tekrar)')})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'patient'
        if commit:
            user.save()
        return user

class AppointmentForm(forms.ModelForm):
    """
    Randevu oluşturma ve düzenleme formu.
    """
    class Meta:
        model = Appointment
        fields = ('patient', 'doctor', 'date', 'time', 'description')
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Sadece hasta tipi kullanıcıları göster
        self.fields['patient'].queryset = User.objects.filter(user_type='patient')
        
        # Sadece doktor tipi kullanıcıları göster
        self.fields['doctor'].queryset = User.objects.filter(user_type='doctor')
        
        # Eğer giriş yapan kullanıcı hasta ise, sadece kendisini seçebilir
        if user and user.is_patient():
            self.fields['patient'].initial = user
            self.fields['patient'].widget = forms.HiddenInput()
            self.fields['date'].help_text = _('Randevu almak istediğiniz tarihi seçiniz')
            self.fields['time'].help_text = _('Randevu almak istediğiniz saati seçiniz')
            self.fields['description'].help_text = _('Randevu sebebinizi kısaca açıklayınız')
        
        # İleri tarihli randevular için kısıtlama ekleyelim
        today = datetime.date.today()
        self.fields['date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')

class TreatmentForm(forms.ModelForm):
    """
    Tedavi oluşturma ve düzenleme formu.
    """
    class Meta:
        model = Treatment
        fields = ('diagnosis', 'notes')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PrescriptionForm(forms.ModelForm):
    """
    Reçete oluşturma ve düzenleme formu.
    """
    medication = forms.ModelChoiceField(
        queryset=Medication.objects.all().order_by('name'),
        label=_('Veritabanından İlaç Seç'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        help_text=_('İlaç veritabanından seçim yaparsanız, ilaç etkileşimleri otomatik kontrol edilir.')
    )
    
    class Meta:
        model = Prescription
        fields = ('medication', 'name', 'dosage', 'instructions')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # İlk gelen instance varsa ve medication değeri doluysa, name alanını doldur
        if self.instance and self.instance.pk and self.instance.medication:
            self.fields['name'].initial = self.instance.medication.name
            self.fields['medication'].initial = self.instance.medication
    
    def clean(self):
        cleaned_data = super().clean()
        medication = cleaned_data.get('medication')
        name = cleaned_data.get('name')
        
        # Eğer ilaç veritabanından seçilmişse, ilaç adını otomatik doldur
        if medication and not name:
            cleaned_data['name'] = medication.name
        
        return cleaned_data

PrescriptionFormSet = forms.inlineformset_factory(
    Treatment, 
    Prescription, 
    form=PrescriptionForm, 
    extra=1, 
    can_delete=True
)

class DoctorCreationForm(forms.ModelForm):
    """
    Doktor oluşturma formu
    """
    password1 = forms.CharField(
        label=_('Şifre'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Şifre')}),
        strip=False,
    )
    password2 = forms.CharField(
        label=_('Şifre (Tekrar)'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Şifre (Tekrar)')}),
        strip=False,
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'specialization', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Kullanıcı Adı')}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ad')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Soyad')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('E-posta')}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Uzmanlık Alanı')}),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Şifreler eşleşmiyor."))
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.user_type = 'doctor'
        if commit:
            user.save()
        return user

class DoctorUpdateForm(forms.ModelForm):
    """
    Doktor güncelleme formu
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'specialization', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ad')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Soyad')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('E-posta')}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Uzmanlık Alanı')}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Telefon')}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Telefon numarası ve uzmanlık alanı zorunlu değil
        self.fields['phone_number'].required = False
        self.fields['specialization'].required = True
        
class MedicalHistoryForm(forms.ModelForm):
    """
    Hasta sağlık geçmişi ekleme ve düzenleme formu.
    """
    class Meta:
        model = MedicalHistory
        fields = ['patient', 'condition_type', 'condition_name', 'diagnosed_date', 'notes', 'is_active']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'condition_type': forms.Select(attrs={'class': 'form-control'}),
            'condition_name': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnosed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece hasta tipi kullanıcıları göster
        self.fields['patient'].queryset = User.objects.filter(user_type='patient') 