"""
AI-Powered Features for MediTracked
"""
import re
from datetime import datetime, timedelta
from django.db.models import Q, Count
from django.utils import timezone
from collections import Counter
import json

from treatments.models import Treatment, Prescription
from treatments.models_lab import LabTest
from treatments.models_medical_history import MedicalHistory
from treatments.models_medications import Medication, MedicationInteraction
from appointments.models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()


class SymptomAnalyzer:
    """
    Semptom analizi ve öneriler
    """
    
    # Semptom-hastalık eşleştirme veritabanı (basit örnek)
    SYMPTOM_DISEASE_MAP = {
        'ateş': ['grip', 'enfeksiyon', 'covid-19', 'bronşit'],
        'öksürük': ['grip', 'bronşit', 'astım', 'covid-19'],
        'nefes darlığı': ['astım', 'covid-19', 'kalp hastalığı', 'akciğer hastalığı'],
        'göğüs ağrısı': ['kalp hastalığı', 'akciğer hastalığı', 'kas ağrısı'],
        'baş ağrısı': ['migren', 'sinüzit', 'gerilim', 'hipertansiyon'],
        'karın ağrısı': ['gastrit', 'ülser', 'apandisit', 'safra taşı'],
        'bulantı': ['gastrit', 'gebelik', 'migren', 'gıda zehirlenmesi'],
        'kusma': ['gastrit', 'gıda zehirlenmesi', 'migren', 'appendisit'],
        'ishal': ['gastroenterit', 'gıda zehirlenmesi', 'ibs', 'enfeksiyon'],
        'yorgunluk': ['anemi', 'depresyon', 'tiroid hastalığı', 'diabetes'],
        'kilo kaybı': ['diabetes', 'hipertiroid', 'kanser', 'depresyon'],
        'kilo alımı': ['hipotiroid', 'diabetes', 'hormon bozukluğu'],
        'eklem ağrısı': ['artrit', 'romatizma', 'gut', 'fibromiyalji'],
        'cilt döküntüsü': ['alerji', 'egzama', 'dermatit', 'mantar enfeksiyonu'],
        'uykusuzluk': ['anksiyete', 'depresyon', 'stres', 'uyku apnesi']
    }
    
    def analyze_symptoms(self, symptoms_text):
        """
        Semptom metnini analiz ederek olası hastalıkları önerir
        """
        if not symptoms_text:
            return []
        
        symptoms_text = symptoms_text.lower()
        found_symptoms = []
        possible_diseases = []
        
        # Semptomlari bul
        for symptom, diseases in self.SYMPTOM_DISEASE_MAP.items():
            if symptom in symptoms_text:
                found_symptoms.append(symptom)
                possible_diseases.extend(diseases)
        
        # En sık görülen hastalıkları say
        disease_counts = Counter(possible_diseases)
        top_diseases = disease_counts.most_common(5)
        
        return {
            'found_symptoms': found_symptoms,
            'possible_diseases': [{'disease': disease, 'confidence': count} for disease, count in top_diseases],
            'recommendations': self.get_general_recommendations(found_symptoms)
        }
    
    def get_general_recommendations(self, symptoms):
        """
        Semptomlara göre genel öneriler
        """
        recommendations = []
        
        if 'ateş' in symptoms:
            recommendations.append('Bol sıvı tüketin ve dinlenin')
            recommendations.append('Ateş 38.5°C üzerindeyse doktora başvurun')
        
        if 'öksürük' in symptoms:
            recommendations.append('Havayı nemlendirecek şekilde ortamı düzenleyin')
            recommendations.append('Öksürük 2 haftadan uzun sürerse doktor kontrolü gerekli')
        
        if 'nefes darlığı' in symptoms:
            recommendations.append('Derhal tıbbi yardım alın - acil durum olabilir')
        
        if 'göğüs ağrısı' in symptoms:
            recommendations.append('Acil servis başvurusu yapın')
        
        if not recommendations:
            recommendations.append('Belirti devam ederse doktor kontrolü önerilir')
        
        return recommendations


class DrugInteractionChecker:
    """
    İlaç etkileşimi kontrolü
    """
    
    def check_prescription_interactions(self, prescription_list):
        """
        Reçete edilen ilaçlar arasında etkileşim kontrolü
        """
        interactions = []
        
        # Her ilaç çifti için etkileşim kontrolü
        for i, med1 in enumerate(prescription_list):
            for med2 in prescription_list[i+1:]:
                interaction = self.check_drug_pair(med1, med2)
                if interaction:
                    interactions.append(interaction)
        
        return interactions
    
    def check_drug_pair(self, medication1, medication2):
        """
        İki ilaç arasında etkileşim kontrolü
        """
        try:
            # Veritabanından etkileşim ara
            interaction = MedicationInteraction.objects.filter(
                Q(medication1__name__icontains=medication1) & Q(medication2__name__icontains=medication2) |
                Q(medication1__name__icontains=medication2) & Q(medication2__name__icontains=medication1)
            ).first()
            
            if interaction:
                return {
                    'medication1': medication1,
                    'medication2': medication2,
                    'severity': interaction.severity,
                    'description': interaction.description,
                    'recommendations': interaction.recommendations
                }
        except Exception:
            pass
        
        return None
    
    def check_patient_drug_history(self, patient, new_medication):
        """
        Hastanın mevcut ilaçları ile yeni ilaç etkileşimi
        """
        # Hastanın aktif ilaçlarını al
        current_medications = MedicalHistory.objects.filter(
            patient=patient,
            condition_type='medication',
            is_active=True
        ).values_list('condition_name', flat=True)
        
        interactions = []
        for current_med in current_medications:
            interaction = self.check_drug_pair(current_med, new_medication)
            if interaction:
                interactions.append(interaction)
        
        return interactions


class TreatmentRecommendationEngine:
    """
    Tedavi önerileri motoru
    """
    
    def get_similar_cases(self, patient_symptoms, patient_age=None, patient_gender=None, limit=5):
        """
        Benzer vakalar bulma
        """
        # Semptom analizi
        analyzer = SymptomAnalyzer()
        analysis = analyzer.analyze_symptoms(patient_symptoms)
        
        if not analysis['possible_diseases']:
            return []
        
        # En olası hastalığa göre benzer tedavileri bul
        top_disease = analysis['possible_diseases'][0]['disease']
        
        similar_treatments = Treatment.objects.filter(
            diagnosis__icontains=top_disease
        ).select_related('appointment__patient').prefetch_related('prescriptions')[:limit]
        
        recommendations = []
        for treatment in similar_treatments:
            recommendations.append({
                'diagnosis': treatment.diagnosis,
                'patient_age': self.calculate_age(treatment.appointment.patient.date_of_birth) if hasattr(treatment.appointment.patient, 'date_of_birth') else None,
                'prescriptions': [
                    {
                        'name': p.name,
                        'dosage': p.dosage,
                        'instructions': p.instructions
                    } for p in treatment.prescriptions.all()
                ],
                'notes': treatment.notes,
                'success_rate': self.calculate_treatment_success_rate(treatment)
            })
        
        return recommendations
    
    def calculate_age(self, birth_date):
        """Yaş hesaplama"""
        if not birth_date:
            return None
        today = timezone.now().date()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def calculate_treatment_success_rate(self, treatment):
        """Tedavi başarı oranı hesaplama (placeholder)"""
        # Bu gerçek verilerle geliştirilebilir
        return 85  # Varsayılan %85 başarı oranı
    
    def recommend_lab_tests(self, symptoms, patient_history=None):
        """
        Semptomlara göre lab testleri önerme
        """
        test_recommendations = []
        
        symptoms_lower = symptoms.lower()
        
        # Semptom-test eşleştirmesi
        if any(word in symptoms_lower for word in ['ateş', 'enfeksiyon', 'yorgunluk']):
            test_recommendations.extend([
                'Tam Kan Sayımı (CBC)',
                'C-Reaktif Protein (CRP)',
                'Sedimentasyon (ESR)'
            ])
        
        if any(word in symptoms_lower for word in ['göğüs ağrısı', 'nefes darlığı']):
            test_recommendations.extend([
                'EKG',
                'Göğüs Röntgeni',
                'Troponin T/I'
            ])
        
        if any(word in symptoms_lower for word in ['karın ağrısı', 'bulantı', 'kusma']):
            test_recommendations.extend([
                'Karaciğer Fonksiyon Testleri',
                'Pankreas Enzimleri',
                'Batın Ultrasonografi'
            ])
        
        if any(word in symptoms_lower for word in ['yorgunluk', 'kilo', 'terleme']):
            test_recommendations.extend([
                'Tiroid Fonksiyon Testleri',
                'HbA1c (Şeker)',
                'Vitamin B12, D'
            ])
        
        return list(set(test_recommendations))  # Duplicateları çıkar


class PatientRiskAssessment:
    """
    Hasta risk değerlendirmesi
    """
    
    def assess_patient_risk(self, patient):
        """
        Hastanın genel risk değerlendirmesi
        """
        risk_factors = []
        risk_score = 0
        
        # Yaş risk faktörü
        age = self.calculate_age(getattr(patient, 'date_of_birth', None))
        if age:
            if age > 65:
                risk_factors.append('Yaş 65 üzeri')
                risk_score += 3
            elif age > 50:
                risk_factors.append('Yaş 50-65 arası')
                risk_score += 2
        
        # Kronik hastalık risk faktörleri
        chronic_conditions = MedicalHistory.objects.filter(
            patient=patient,
            condition_type='chronic',
            is_active=True
        )
        
        high_risk_conditions = ['diabetes', 'hipertansiyon', 'kalp hastalığı', 'copd', 'astım']
        for condition in chronic_conditions:
            condition_name = condition.condition_name.lower()
            if any(hrc in condition_name for hrc in high_risk_conditions):
                risk_factors.append(f'Kronik hastalık: {condition.condition_name}')
                risk_score += 2
        
        # Alerji risk faktörleri
        allergies = MedicalHistory.objects.filter(
            patient=patient,
            condition_type='allergy',
            is_active=True
        ).count()
        
        if allergies > 0:
            risk_factors.append(f'{allergies} adet aktif alerji')
            risk_score += 1
        
        # Risk seviyesi belirleme
        if risk_score >= 6:
            risk_level = 'Yüksek'
            color = 'danger'
        elif risk_score >= 3:
            risk_level = 'Orta'
            color = 'warning'
        else:
            risk_level = 'Düşük'
            color = 'success'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': color,
            'risk_factors': risk_factors,
            'recommendations': self.get_risk_recommendations(risk_level, risk_factors)
        }
    
    def calculate_age(self, birth_date):
        """Yaş hesaplama"""
        if not birth_date:
            return None
        today = timezone.now().date()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def get_risk_recommendations(self, risk_level, risk_factors):
        """
        Risk seviyesine göre öneriler
        """
        recommendations = []
        
        if risk_level == 'Yüksek':
            recommendations.extend([
                'Düzenli doktor kontrolleri (3 ayda bir)',
                'Acil durum planı hazırlayın',
                'İlaç uyumuna dikkat edin',
                'Yaşam tarzı değişiklikleri yapın'
            ])
        elif risk_level == 'Orta':
            recommendations.extend([
                'Düzenli kontroller (6 ayda bir)',
                'Sağlıklı beslenme programı',
                'Düzenli egzersiz yapın'
            ])
        else:
            recommendations.extend([
                'Yıllık kontroller yeterli',
                'Sağlıklı yaşam tarzını sürdürün',
                'Preventif bakıma odaklanın'
            ])
        
        return recommendations


class AIHealthInsights:
    """
    AI destekli sağlık içgörüleri
    """
    
    def __init__(self):
        self.symptom_analyzer = SymptomAnalyzer()
        self.drug_checker = DrugInteractionChecker()
        self.treatment_engine = TreatmentRecommendationEngine()
        self.risk_assessor = PatientRiskAssessment()
    
    def generate_patient_insights(self, patient):
        """
        Hasta için kapsamlı AI analizi
        """
        insights = {
            'patient': patient,
            'risk_assessment': self.risk_assessor.assess_patient_risk(patient),
            'recent_treatments': self.analyze_recent_treatments(patient),
            'medication_reminders': self.get_medication_reminders(patient),
            'upcoming_care_suggestions': self.suggest_upcoming_care(patient)
        }
        
        return insights
    
    def analyze_recent_treatments(self, patient):
        """
        Son tedavileri analiz et
        """
        recent_treatments = Treatment.objects.filter(
            appointment__patient=patient
        ).order_by('-created_at')[:5]
        
        analysis = {
            'total_treatments': recent_treatments.count(),
            'common_diagnoses': [],
            'treatment_patterns': [],
            'suggestions': []
        }
        
        if recent_treatments:
            # En sık görülen teşhisler
            diagnoses = [t.diagnosis for t in recent_treatments]
            diagnosis_counts = Counter(diagnoses)
            analysis['common_diagnoses'] = diagnosis_counts.most_common(3)
            
            # Tedavi kalıpları
            if len(recent_treatments) >= 3:
                analysis['treatment_patterns'].append('Düzenli takip gösteriyor')
            
            # Öneriler
            if diagnosis_counts.most_common(1)[0][1] > 1:
                analysis['suggestions'].append('Tekrarlayan şikayet için önleyici tedavi değerlendirin')
        
        return analysis
    
    def get_medication_reminders(self, patient):
        """
        İlaç hatırlatmaları
        """
        active_medications = MedicalHistory.objects.filter(
            patient=patient,
            condition_type='medication',
            is_active=True
        )
        
        reminders = []
        for med in active_medications:
            reminders.append({
                'medication': med.condition_name,
                'start_date': med.diagnosed_date,
                'notes': med.notes,
                'duration_days': (timezone.now().date() - med.diagnosed_date).days if med.diagnosed_date else 0
            })
        
        return reminders
    
    def suggest_upcoming_care(self, patient):
        """
        Gelecek bakım önerileri
        """
        suggestions = []
        
        # Son randevu tarihi
        last_appointment = Appointment.objects.filter(
            patient=patient,
            status='completed'
        ).order_by('-date').first()
        
        if last_appointment:
            days_since_last = (timezone.now().date() - last_appointment.date).days
            
            if days_since_last > 365:
                suggestions.append({
                    'type': 'Genel Kontrol',
                    'urgency': 'Yüksek',
                    'description': 'Yıllık genel kontrol zamanı geldi'
                })
            elif days_since_last > 180:
                suggestions.append({
                    'type': 'Takip Randevusu',
                    'urgency': 'Orta',
                    'description': 'Altı aylık takip kontrolü'
                })
        
        # Kronik hastalık takibi
        chronic_conditions = MedicalHistory.objects.filter(
            patient=patient,
            condition_type='chronic',
            is_active=True
        )
        
        for condition in chronic_conditions:
            suggestions.append({
                'type': 'Kronik Hastalık Takibi',
                'urgency': 'Orta',
                'description': f'{condition.condition_name} için kontrol'
            })
        
        return suggestions
