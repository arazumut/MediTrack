from django.urls import path
from . import views

app_name = 'telemedicine'

urlpatterns = [
    # Konsültasyonlar
    path('', views.TeleMedicineConsultationListView.as_view(), name='list'),
    path('consultations/<int:pk>/', views.TeleMedicineConsultationDetailView.as_view(), name='detail'),
    path('consultations/<uuid:meeting_id>/join/', views.join_consultation, name='join'),
    path('consultations/<int:appointment_id>/create/', views.create_telemedicine_consultation, name='create'),
    path('consultations/<int:consultation_id>/messages/', views.get_consultation_messages, name='get_messages'),
    path('consultations/<int:consultation_id>/messages/send/', views.send_consultation_message, name='send_message'),
    path('consultations/<int:consultation_id>/end/', views.end_consultation, name='end'),
    path('consultations/<int:consultation_id>/status/', views.update_consultation_status, name='update_status'),
    path('analytics/', views.consultation_analytics, name='analytics'),
    path('dashboard/', views.telemedicine_dashboard, name='dashboard'),

    # Telemedicine randevuları ve oturumlar
    path('appointments/', views.TelemedicineAppointmentListView.as_view(), name='appointment-list'),
    path('appointments/create/', views.create_telemedicine_appointment, name='appointment-create'),
    path('appointments/<int:pk>/', views.TelemedicineAppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:appointment_id>/start-session/', views.start_video_session, name='start-session'),
    path('sessions/<int:session_id>/end/', views.end_video_session, name='end-session'),

    # Ayarlar
    path('settings/', views.TeleMedicineSettingsView.as_view(), name='settings'),
]
