from django.urls import path
from . import views

app_name = 'telemedicine'

urlpatterns = [
    # Main views
    path('', views.TeleMedicineConsultationListView.as_view(), name='list'),
    path('session/<str:meeting_id>/', views.TeleMedicineConsultationDetailView.as_view(), name='detail'),
    path('settings/', views.TeleMedicineSettingsView.as_view(), name='settings'),
]
