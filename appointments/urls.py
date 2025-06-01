from django.urls import path
from .views_availability import (
    DoctorAvailabilityListView, DoctorAvailabilityCreateView, 
    DoctorAvailabilityUpdateView, DoctorAvailabilityDeleteView,
    DoctorTimeOffListView, DoctorTimeOffCreateView,
    DoctorTimeOffUpdateView, DoctorTimeOffDeleteView,
    DoctorCalendarView
)

urlpatterns = [
    # Doktor Çalışma Saatleri
    path('doctors/<int:doctor_id>/availability/', DoctorAvailabilityListView.as_view(), name='doctor-availability-list'),
    path('doctors/<int:doctor_id>/availability/create/', DoctorAvailabilityCreateView.as_view(), name='doctor-availability-create'),
    path('availability/<int:pk>/update/', DoctorAvailabilityUpdateView.as_view(), name='doctor-availability-update'),
    path('availability/<int:pk>/delete/', DoctorAvailabilityDeleteView.as_view(), name='doctor-availability-delete'),
    
    # Doktor İzin Günleri
    path('doctors/<int:doctor_id>/timeoff/', DoctorTimeOffListView.as_view(), name='doctor-timeoff-list'),
    path('doctors/<int:doctor_id>/timeoff/create/', DoctorTimeOffCreateView.as_view(), name='doctor-timeoff-create'),
    path('timeoff/<int:pk>/update/', DoctorTimeOffUpdateView.as_view(), name='doctor-timeoff-update'),
    path('timeoff/<int:pk>/delete/', DoctorTimeOffDeleteView.as_view(), name='doctor-timeoff-delete'),
    
    # Doktor Takvimi
    path('doctors/<int:doctor_id>/calendar/', DoctorCalendarView.as_view(), name='doctor-calendar'),
]
