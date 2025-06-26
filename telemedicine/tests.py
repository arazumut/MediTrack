# Run tests with: python manage.py test telemedicine

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import TeleconsultationSession, TeleconsultationMessage, TeleconsultationSettings

User = get_user_model()


class TeleconsultationModelsTest(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            username='patient_test',
            email='patient@test.com',
            password='testpass123',
            user_type='patient'
        )
        self.doctor = User.objects.create_user(
            username='doctor_test',
            email='doctor@test.com',
            password='testpass123',
            user_type='doctor'
        )

    def test_teleconsultation_session_creation(self):
        session = TeleconsultationSession.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_time=timezone.now() + timedelta(hours=1),
            duration_minutes=30,
            session_type='video'
        )
        self.assertTrue(session.session_id)
        self.assertEqual(session.status, 'scheduled')
        self.assertEqual(session.duration_minutes, 30)

    def test_teleconsultation_message_creation(self):
        session = TeleconsultationSession.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_time=timezone.now() + timedelta(hours=1)
        )
        message = TeleconsultationMessage.objects.create(
            session=session,
            sender=self.patient,
            content='Hello doctor',
            message_type='text'
        )
        self.assertEqual(message.content, 'Hello doctor')
        self.assertEqual(message.sender, self.patient)

    def test_teleconsultation_settings_creation(self):
        settings = TeleconsultationSettings.objects.create(
            user=self.patient,
            enable_video=True,
            enable_audio=True
        )
        self.assertTrue(settings.enable_video)
        self.assertTrue(settings.enable_audio)


class TeleconsultationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(
            username='patient_test',
            email='patient@test.com',
            password='testpass123',
            user_type='patient'
        )
        self.doctor = User.objects.create_user(
            username='doctor_test',
            email='doctor@test.com',
            password='testpass123',
            user_type='doctor'
        )

    def test_teleconsultation_list_view_authenticated(self):
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(reverse('telemedicine:list'))
        self.assertEqual(response.status_code, 200)

    def test_teleconsultation_list_view_unauthenticated(self):
        response = self.client.get(reverse('telemedicine:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_teleconsultation_schedule_view(self):
        self.client.login(username='patient_test', password='testpass123')
        response = self.client.get(reverse('telemedicine:schedule'))
        self.assertEqual(response.status_code, 200)

    def test_teleconsultation_session_detail(self):
        self.client.login(username='patient_test', password='testpass123')
        session = TeleconsultationSession.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_time=timezone.now() + timedelta(hours=1)
        )
        response = self.client.get(reverse('telemedicine:detail', kwargs={'session_id': session.session_id}))
        self.assertEqual(response.status_code, 200)


class TeleconsultationIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(
            username='patient_test',
            email='patient@test.com',
            password='testpass123',
            user_type='patient'
        )
        self.doctor = User.objects.create_user(
            username='doctor_test',
            email='doctor@test.com',
            password='testpass123',
            user_type='doctor'
        )

    def test_full_consultation_flow(self):
        # Login as patient
        self.client.login(username='patient_test', password='testpass123')
        
        # Create session
        session = TeleconsultationSession.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_time=timezone.now() + timedelta(hours=1)
        )
        
        # Join session
        response = self.client.get(reverse('telemedicine:join', kwargs={'session_id': session.session_id}))
        self.assertEqual(response.status_code, 200)
        
        # Send message
        response = self.client.post(reverse('telemedicine:send_message', kwargs={'session_id': session.session_id}), {
            'content': 'Hello doctor'
        })
        self.assertEqual(response.status_code, 200)
        
        # Check message was created
        messages = TeleconsultationMessage.objects.filter(session=session)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().content, 'Hello doctor')
