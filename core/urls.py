from django.urls import path
from . import views

urlpatterns = [
    # Hastalar
    path('patients/register/', views.PatientRegistrationView.as_view(), name='patient-register'),
    path('patients/', views.PatientListView.as_view(), name='patient-list'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient-detail'),
    
    # Doktorlar
    path('doctors/', views.DoctorListView.as_view(), name='doctor-list'),
    
    # Randevular
    path('appointments/', views.AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:pk>/update/', views.AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointments/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment-delete'),
    
    # Tedaviler
    path('appointments/<int:appointment_id>/treatment/create/', views.TreatmentCreateView.as_view(), name='treatment-create'),
    path('treatments/<int:pk>/', views.TreatmentDetailView.as_view(), name='treatment-detail'),
    path('treatments/<int:pk>/update/', views.TreatmentUpdateView.as_view(), name='treatment-update'),
] 