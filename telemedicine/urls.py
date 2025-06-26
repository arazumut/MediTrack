from django.urls import path
from . import views

app_name = 'telemedicine'

urlpatterns = [
    # Main views
    path('', views.TeleconsultationListView.as_view(), name='list'),
    path('schedule/', views.TeleconsultationCreateView.as_view(), name='schedule'),
    path('session/<str:session_id>/', views.TeleconsultationDetailView.as_view(), name='detail'),
    path('session/<str:session_id>/join/', views.TeleconsultationJoinView.as_view(), name='join'),
    path('session/<str:session_id>/end/', views.TeleconsultationEndView.as_view(), name='end'),
    
    # AJAX/API views
    path('session/<str:session_id>/send-message/', views.send_message, name='send_message'),
    path('session/<str:session_id>/get-messages/', views.get_messages, name='get_messages'),
    path('session/<str:session_id>/update-status/', views.update_session_status, name='update_status'),
    
    # Settings
    path('settings/', views.TeleconsultationSettingsView.as_view(), name='settings'),
    
    # Analytics
    path('analytics/', views.TeleconsultationAnalyticsView.as_view(), name='analytics'),
    
    # WebRTC signaling (for future implementation)
    path('session/<str:session_id>/signal/', views.webrtc_signal, name='webrtc_signal'),
]
