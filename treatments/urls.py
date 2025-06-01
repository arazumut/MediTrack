from django.urls import path
from .views_lab import (
    LabTestListView, LabTestDetailView, LabTestCreateView, 
    LabTestUpdateView, LabTestDeleteView, 
    TestResultCreateView, TestResultUpdateView
)
from .views_medications import (
    MedicationListView, MedicationDetailView, MedicationCreateView, 
    MedicationUpdateView, MedicationDeleteView,
    InteractionListView, InteractionDetailView, InteractionCreateView,
    InteractionUpdateView, InteractionDeleteView,
    patient_medications, medication_search_api
)
from .views_imaging import (
    MedicalImageListView, MedicalImageDetailView, MedicalImageCreateView,
    MedicalImageUpdateView, MedicalImageDeleteView, serve_medical_image,
    ReportListView, ReportDetailView, ReportCreateView,
    ReportUpdateView, ReportDeleteView, serve_report_file
)

urlpatterns = [
    # Laboratuvar Testleri
    path('lab-tests/', LabTestListView.as_view(), name='lab-test-list'),
    path('patients/<int:patient_id>/lab-tests/', LabTestListView.as_view(), name='lab-test-list'),
    path('treatments/<int:treatment_id>/lab-tests/create/', LabTestCreateView.as_view(), name='lab-test-create'),
    path('patients/<int:patient_id>/lab-tests/create/', LabTestCreateView.as_view(), name='lab-test-create'),
    path('lab-tests/<int:pk>/', LabTestDetailView.as_view(), name='lab-test-detail'),
    path('lab-tests/<int:pk>/update/', LabTestUpdateView.as_view(), name='lab-test-update'),
    path('lab-tests/<int:pk>/delete/', LabTestDeleteView.as_view(), name='lab-test-delete'),
    
    # Test Sonuçları
    path('lab-tests/<int:lab_test_id>/results/create/', TestResultCreateView.as_view(), name='test-result-create'),
    path('test-results/<int:pk>/update/', TestResultUpdateView.as_view(), name='test-result-update'),
    
    # İlaç Yönetimi
    path('medications/', MedicationListView.as_view(), name='medication_list'),
    path('medications/<int:pk>/', MedicationDetailView.as_view(), name='medication_detail'),
    path('medications/create/', MedicationCreateView.as_view(), name='medication_create'),
    path('medications/<int:pk>/update/', MedicationUpdateView.as_view(), name='medication_update'),
    path('medications/<int:pk>/delete/', MedicationDeleteView.as_view(), name='medication_delete'),
    
    # İlaç Etkileşimleri
    path('interactions/', InteractionListView.as_view(), name='interaction_list'),
    path('interactions/<int:pk>/', InteractionDetailView.as_view(), name='interaction_detail'),
    path('interactions/create/', InteractionCreateView.as_view(), name='interaction_create'),
    path('interactions/<int:pk>/update/', InteractionUpdateView.as_view(), name='interaction_update'),
    path('interactions/<int:pk>/delete/', InteractionDeleteView.as_view(), name='interaction_delete'),
    
    # Hasta İlaçları
    path('patients/<int:patient_id>/medications/', patient_medications, name='patient_medications'),
    path('api/medications/search/', medication_search_api, name='medication_search_api'),
    
    # Tıbbi Görüntülemeler
    path('medical-images/', MedicalImageListView.as_view(), name='medical-image-list'),
    path('patients/<int:patient_id>/medical-images/', MedicalImageListView.as_view(), name='medical-image-list'),
    path('treatments/<int:treatment_id>/medical-images/', MedicalImageListView.as_view(), name='medical-image-list'),
    path('treatments/<int:treatment_id>/medical-images/create/', MedicalImageCreateView.as_view(), name='medical-image-create'),
    path('patients/<int:patient_id>/medical-images/create/', MedicalImageCreateView.as_view(), name='medical-image-create'),
    path('medical-images/<int:pk>/', MedicalImageDetailView.as_view(), name='medical-image-detail'),
    path('medical-images/<int:pk>/update/', MedicalImageUpdateView.as_view(), name='medical-image-update'),
    path('medical-images/<int:pk>/delete/', MedicalImageDeleteView.as_view(), name='medical-image-delete'),
    path('medical-images/<int:pk>/file/', serve_medical_image, name='serve-medical-image'),
    
    # Raporlar
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('patients/<int:patient_id>/reports/', ReportListView.as_view(), name='report-list'),
    path('treatments/<int:treatment_id>/reports/', ReportListView.as_view(), name='report-list'),
    path('treatments/<int:treatment_id>/reports/create/', ReportCreateView.as_view(), name='report-create'),
    path('patients/<int:patient_id>/reports/create/', ReportCreateView.as_view(), name='report-create'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/update/', ReportUpdateView.as_view(), name='report-update'),
    path('reports/<int:pk>/delete/', ReportDeleteView.as_view(), name='report-delete'),
    path('reports/<int:pk>/file/', serve_report_file, name='serve-report-file'),
]
