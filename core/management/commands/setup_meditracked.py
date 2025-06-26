from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random

from core.models_notifications import NotificationType, NotificationTemplate
from core.models_i18n import Language, MedicalTerminology
from telemedicine.models import TeleconsultationSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize MediTracked system with sample data and configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )
        parser.add_argument(
            '--sample-data',
            action='store_true',
            help='Create sample data for testing',
        )
        parser.add_argument(
            '--setup-notifications',
            action='store_true',
            help='Setup notification templates',
        )
        parser.add_argument(
            '--setup-languages',
            action='store_true',
            help='Setup multi-language support',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all setup tasks',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Initializing MediTracked System...'))
        
        if options['all']:
            options['create_superuser'] = True
            options['sample_data'] = True
            options['setup_notifications'] = True
            options['setup_languages'] = True

        try:
            with transaction.atomic():
                if options['create_superuser']:
                    self.create_superuser()
                    
                if options['setup_notifications']:
                    self.setup_notifications()
                    
                if options['setup_languages']:
                    self.setup_languages()
                    
                if options['sample_data']:
                    self.create_sample_data()
                    
            self.stdout.write(self.style.SUCCESS('✅ MediTracked system initialized successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during initialization: {str(e)}'))
            raise

    def create_superuser(self):
        """Create admin superuser if it doesn't exist"""
        self.stdout.write('👤 Setting up admin user...')
        
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@meditracked.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                user_type='admin',
                phone='555-0000'
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Admin user created: admin/admin123'))
        else:
            self.stdout.write('ℹ️  Admin user already exists')

    def setup_notifications(self):
        """Setup notification types and templates"""
        self.stdout.write('📬 Setting up notification system...')
        
        # Notification Types
        notification_types = [
            {
                'name': 'appointment_reminder',
                'display_name': 'Appointment Reminder',
                'description': 'Reminders for upcoming appointments',
                'default_enabled': True,
                'priority': 'medium'
            },
            {
                'name': 'telemedicine_invitation',
                'display_name': 'Telemedicine Invitation',
                'description': 'Invitations to join teleconsultation',
                'default_enabled': True,
                'priority': 'high'
            },
            {
                'name': 'ai_health_alert',
                'display_name': 'AI Health Alert',
                'description': 'AI-generated health recommendations',
                'default_enabled': True,
                'priority': 'high'
            },
            {
                'name': 'lab_results',
                'display_name': 'Lab Results Available',
                'description': 'Laboratory test results ready',
                'default_enabled': True,
                'priority': 'medium'
            },
            {
                'name': 'medication_reminder',
                'display_name': 'Medication Reminder',
                'description': 'Medication intake reminders',
                'default_enabled': True,
                'priority': 'medium'
            }
        ]
        
        for nt_data in notification_types:
            nt, created = NotificationType.objects.get_or_create(
                name=nt_data['name'],
                defaults=nt_data
            )
            if created:
                self.stdout.write(f'  ✅ Created notification type: {nt.display_name}')

        # Notification Templates
        templates = [
            {
                'notification_type': NotificationType.objects.get(name='appointment_reminder'),
                'name': 'default_appointment_reminder',
                'subject': 'Appointment Reminder - {{appointment_date}}',
                'message': 'Hello {{patient_name}}, you have an appointment with Dr. {{doctor_name}} on {{appointment_date}} at {{appointment_time}}.',
                'is_default': True
            },
            {
                'notification_type': NotificationType.objects.get(name='telemedicine_invitation'),
                'name': 'default_telemedicine_invitation',
                'subject': 'Teleconsultation Invitation',
                'message': 'Dr. {{doctor_name}} has invited you to a teleconsultation. Session ID: {{session_id}}. Join at: {{join_url}}',
                'is_default': True
            },
            {
                'notification_type': NotificationType.objects.get(name='ai_health_alert'),
                'name': 'default_ai_alert',
                'subject': 'AI Health Recommendation',
                'message': 'Based on your health data analysis, we recommend: {{recommendation}}. Please consult with your doctor.',
                'is_default': True
            }
        ]
        
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'  ✅ Created notification template: {template.name}')

    def setup_languages(self):
        """Setup multi-language support"""
        self.stdout.write('🌍 Setting up multi-language support...')
        
        languages = [
            {'code': 'tr', 'name': 'Türkçe', 'native_name': 'Türkçe', 'is_active': True},
            {'code': 'en', 'name': 'English', 'native_name': 'English', 'is_active': True},
            {'code': 'ar', 'name': 'Arabic', 'native_name': 'العربية', 'is_active': True},
            {'code': 'de', 'name': 'German', 'native_name': 'Deutsch', 'is_active': True},
            {'code': 'fr', 'name': 'French', 'native_name': 'Français', 'is_active': True},
        ]
        
        for lang_data in languages:
            lang, created = Language.objects.get_or_create(
                code=lang_data['code'],
                defaults=lang_data
            )
            if created:
                self.stdout.write(f'  ✅ Added language: {lang.name}')

        # Medical Terminology
        medical_terms = [
            {
                'term_key': 'appointment',
                'language': Language.objects.get(code='tr'),
                'translation': 'randevu',
                'category': 'general'
            },
            {
                'term_key': 'appointment',
                'language': Language.objects.get(code='en'),
                'translation': 'appointment',
                'category': 'general'
            },
            {
                'term_key': 'doctor',
                'language': Language.objects.get(code='tr'),
                'translation': 'doktor',
                'category': 'personnel'
            },
            {
                'term_key': 'doctor',
                'language': Language.objects.get(code='en'),
                'translation': 'doctor',
                'category': 'personnel'
            },
            {
                'term_key': 'patient',
                'language': Language.objects.get(code='tr'),
                'translation': 'hasta',
                'category': 'personnel'
            },
            {
                'term_key': 'patient',
                'language': Language.objects.get(code='en'),
                'translation': 'patient',
                'category': 'personnel'
            },
            {
                'term_key': 'prescription',
                'language': Language.objects.get(code='tr'),
                'translation': 'reçete',
                'category': 'medical'
            },
            {
                'term_key': 'prescription',
                'language': Language.objects.get(code='en'),
                'translation': 'prescription',
                'category': 'medical'
            }
        ]
        
        for term_data in medical_terms:
            term, created = MedicalTerminology.objects.get_or_create(
                term_key=term_data['term_key'],
                language=term_data['language'],
                defaults=term_data
            )
            if created:
                self.stdout.write(f'  ✅ Added medical term: {term.term_key} ({term.language.code})')

    def create_sample_data(self):
        """Create sample users and data for testing"""
        self.stdout.write('🧪 Creating sample data...')
        
        # Sample Doctors
        doctors_data = [
            {
                'username': 'dr_sarah',
                'email': 'sarah@meditracked.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'user_type': 'doctor',
                'department': 'Cardiology',
                'phone': '555-1001'
            },
            {
                'username': 'dr_michael',
                'email': 'michael@meditracked.com',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'user_type': 'doctor',
                'department': 'Neurology',
                'phone': '555-1002'
            },
            {
                'username': 'dr_emma',
                'email': 'emma@meditracked.com',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'user_type': 'doctor',
                'department': 'Pediatrics',
                'phone': '555-1003'
            }
        ]
        
        for doctor_data in doctors_data:
            if not User.objects.filter(username=doctor_data['username']).exists():
                doctor = User.objects.create_user(
                    password='doctor123',
                    **doctor_data
                )
                
                # Create telemedicine settings for doctors
                TeleconsultationSettings.objects.create(
                    user=doctor,
                    enable_video=True,
                    enable_audio=True,
                    enable_screen_share=True,
                    enable_chat=True,
                    auto_record=True
                )
                
                self.stdout.write(f'  ✅ Created doctor: {doctor.get_full_name()} ({doctor.username})')

        # Sample Patients
        patients_data = [
            {
                'username': 'patient_john',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_type': 'patient',
                'phone': '555-2001'
            },
            {
                'username': 'patient_jane',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'user_type': 'patient',
                'phone': '555-2002'
            },
            {
                'username': 'patient_bob',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'user_type': 'patient',
                'phone': '555-2003'
            }
        ]
        
        for patient_data in patients_data:
            if not User.objects.filter(username=patient_data['username']).exists():
                patient = User.objects.create_user(
                    password='patient123',
                    **patient_data
                )
                
                # Create telemedicine settings for patients
                TeleconsultationSettings.objects.create(
                    user=patient,
                    enable_video=True,
                    enable_audio=True,
                    enable_chat=True
                )
                
                self.stdout.write(f'  ✅ Created patient: {patient.get_full_name()} ({patient.username})')

        # Sample Receptionist
        if not User.objects.filter(username='receptionist').exists():
            receptionist = User.objects.create_user(
                username='receptionist',
                email='receptionist@meditracked.com',
                password='receptionist123',
                first_name='Alice',
                last_name='Brown',
                user_type='receptionist',
                phone='555-3001'
            )
            self.stdout.write(f'  ✅ Created receptionist: {receptionist.get_full_name()}')

        self.stdout.write(self.style.WARNING('📝 Sample Data Credentials:'))
        self.stdout.write('  Admin: admin/admin123')
        self.stdout.write('  Doctors: dr_sarah/doctor123, dr_michael/doctor123, dr_emma/doctor123')
        self.stdout.write('  Patients: patient_john/patient123, patient_jane/patient123, patient_bob/patient123')
        self.stdout.write('  Receptionist: receptionist/receptionist123')
