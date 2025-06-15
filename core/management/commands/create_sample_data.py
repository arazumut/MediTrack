import random
from datetime import datetime, timedelta, time
import pytz
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from appointments.models_availability import DoctorAvailability, DoctorTimeOff
from treatments.models import Treatment, Prescription
from treatments.models_medical_history import MedicalHistory
from core.models_communication import Notification
from treatments.models_medications import Medication
from treatments.models_lab import LabTest, TestResult
from treatments.models_imaging import MedicalImage, Report

User = get_user_model()

# Doktor uzmanlık alanları
SPECIALIZATIONS = [
    'Dahiliye', 'Kardiyoloji', 'Göz Hastalıkları', 'Ortopedi', 'Nöroloji',
    'Dermatoloji', 'Üroloji', 'Kulak Burun Boğaz', 'Genel Cerrahi', 'Kadın Hastalıkları ve Doğum',
    'Çocuk Sağlığı ve Hastalıkları', 'Psikiyatri', 'Fizik Tedavi ve Rehabilitasyon'
]

# Hasta kan grupları
BLOOD_TYPES = ['A Rh+', 'A Rh-', 'B Rh+', 'B Rh-', 'AB Rh+', 'AB Rh-', '0 Rh+', '0 Rh-']

# İl ve ilçeler (örnek olarak birkaç tane eklenmiştir)
CITIES_AND_DISTRICTS = [
    {'city': 'İstanbul', 'districts': ['Kadıköy', 'Beşiktaş', 'Şişli', 'Üsküdar', 'Beyoğlu']},
    {'city': 'Ankara', 'districts': ['Çankaya', 'Keçiören', 'Mamak', 'Yenimahalle', 'Etimesgut']},
    {'city': 'İzmir', 'districts': ['Konak', 'Karşıyaka', 'Bornova', 'Bayraklı', 'Buca']},
    {'city': 'Bursa', 'districts': ['Osmangazi', 'Nilüfer', 'Yıldırım', 'Gemlik', 'İnegöl']},
    {'city': 'Antalya', 'districts': ['Muratpaşa', 'Konyaaltı', 'Kepez', 'Alanya', 'Manavgat']}
]

# Tedavi teşhisleri
DIAGNOSES = [
    'Grip', 'Soğuk Algınlığı', 'Migren', 'Hipertansiyon', 'Diyabet', 
    'Anemi', 'Bel Fıtığı', 'Boyun Fıtığı', 'Gastrit', 'Reflü',
    'Astım', 'Bronşit', 'Sinüzit', 'Kulak İltihabı', 'Farenjit',
    'Egzama', 'Sedef Hastalığı', 'Alerji', 'Vertigo', 'Anksiyete'
]

# İlaçlar ve kullanım talimatları
MEDICATIONS = [
    {
        'name': 'Parol',
        'dosage': '500 mg',
        'instructions': 'Günde 3 defa, aç karnına alınmamalıdır.'
    },
    {
        'name': 'Aspirin',
        'dosage': '100 mg',
        'instructions': 'Günde 1 defa, yemeklerden sonra alınmalıdır.'
    },
    {
        'name': 'Nurofen',
        'dosage': '400 mg',
        'instructions': 'Günde 2 defa, 12 saat arayla alınmalıdır.'
    },
    {
        'name': 'Augmentin',
        'dosage': '1000 mg',
        'instructions': 'Günde 2 defa, 12 saat arayla, yemeklerden önce alınmalıdır.'
    },
    {
        'name': 'Ventolin',
        'dosage': '100 mcg',
        'instructions': 'Günde 2 defa, 2 inhalasyon olarak uygulanmalıdır.'
    },
    {
        'name': 'Nexium',
        'dosage': '40 mg',
        'instructions': 'Günde 1 defa, sabah aç karnına alınmalıdır.'
    },
    {
        'name': 'Cipralex',
        'dosage': '10 mg',
        'instructions': 'Günde 1 defa, akşam yemeğinden sonra alınmalıdır.'
    },
    {
        'name': 'Euthyrox',
        'dosage': '50 mcg',
        'instructions': 'Günde 1 defa, sabah aç karnına, kahvaltıdan 30 dakika önce alınmalıdır.'
    },
    {
        'name': 'Concor',
        'dosage': '5 mg',
        'instructions': 'Günde 1 defa, sabah kahvaltıdan sonra alınmalıdır.'
    },
    {
        'name': 'Xyzal',
        'dosage': '5 mg',
        'instructions': 'Günde 1 defa, akşam yemeklerinden sonra alınmalıdır.'
    }
]

class Command(BaseCommand):
    help = 'MediTrack sistemi için örnek veriler oluşturur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--patients',
            type=int,
            default=20,
            help='Oluşturulacak hasta sayısı'
        )
        parser.add_argument(
            '--doctors',
            type=int,
            default=10,
            help='Oluşturulacak doktor sayısı'
        )
        parser.add_argument(
            '--appointments',
            type=int,
            default=50,
            help='Oluşturulacak randevu sayısı'
        )
        parser.add_argument(
            '--treatments',
            type=int,
            default=30,
            help='Oluşturulacak tedavi sayısı'
        )
        parser.add_argument(
            '--availabilities',
            type=int,
            default=20,
            help='Oluşturulacak doktor uygunluğu sayısı'
        )
        parser.add_argument(
            '--timeoffs',
            type=int,
            default=15,
            help='Oluşturulacak doktor izin sayısı'
        )
        parser.add_argument(
            '--medicalhistories',
            type=int,
            default=25,
            help='Oluşturulacak tıbbi geçmiş sayısı'
        )
        parser.add_argument(
            '--notifications',
            type=int,
            default=40,
            help='Oluşturulacak bildirim sayısı'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('MediTrack örnek veri oluşturma başlatılıyor...'))
        
        # Admin kullanıcısı oluştur
        self.create_admin_user()
        
        # Resepsiyonist oluştur
        self.create_receptionists()
        
        # Doktorlar oluştur
        num_doctors = options['doctors']
        doctors = self.create_doctors(num_doctors)
        
        # Hastalar oluştur
        num_patients = options['patients']
        patients = self.create_patients(num_patients)
        
        # Doktor uygunlukları oluştur
        num_availabilities = options['availabilities']
        self.create_doctor_availabilities(num_availabilities, doctors)
        
        # Doktor izinleri oluştur
        num_timeoffs = options['timeoffs']
        self.create_doctor_timeoffs(num_timeoffs, doctors)
        
        # Randevular oluştur
        num_appointments = options['appointments']
        appointments = self.create_appointments(num_appointments, doctors, patients)
        
        # Tedaviler ve reçeteler oluştur
        num_treatments = options['treatments']
        treatments = self.create_treatments_and_prescriptions(num_treatments, appointments)
        
        # Tıbbi geçmişler oluştur
        num_medicalhistories = options['medicalhistories']
        self.create_medical_histories(num_medicalhistories, patients)
        
        # Laboratuvar testleri ve sonuçları oluştur
        self.create_lab_tests_and_results(doctors, patients)
        
        # Görüntüleme ve sonuçları oluştur
        self.create_imaging_and_results(doctors, patients)
        
        # Bildirimler oluştur
        num_notifications = options['notifications']
        self.create_notifications(num_notifications)
        
        self.stdout.write(self.style.SUCCESS('Örnek veriler başarıyla oluşturuldu!'))
        self.stdout.write(f'- {num_doctors} doktor')
        self.stdout.write(f'- {num_patients} hasta')
        self.stdout.write(f'- {num_availabilities} doktor uygunluğu')
        self.stdout.write(f'- {num_timeoffs} doktor izni')
        self.stdout.write(f'- {num_appointments} randevu')
        self.stdout.write(f'- {num_treatments} tedavi ve reçete')
        self.stdout.write(f'- {num_medicalhistories} tıbbi geçmiş kaydı')
        self.stdout.write(f'- {num_notifications} bildirim')

    def create_admin_user(self):
        """Admin kullanıcısı oluşturur."""
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@meditrack.com',
                'first_name': 'Admin',
                'last_name': 'Kullanıcı',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin kullanıcısı oluşturuldu'))
        else:
            self.stdout.write(self.style.WARNING('Admin kullanıcısı zaten mevcut'))

    def create_receptionists(self):
        """Resepsiyonist kullanıcıları oluşturur."""
        receptionist_data = [
            {
                'username': 'ayse',
                'email': 'ayse@meditrack.com',
                'first_name': 'Ayşe',
                'last_name': 'Yılmaz',
                'password': 'password123'
            },
            {
                'username': 'mehmet',
                'email': 'mehmet@meditrack.com',
                'first_name': 'Mehmet',
                'last_name': 'Demir',
                'password': 'password123'
            }
        ]
        
        created_count = 0
        for data in receptionist_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'user_type': 'receptionist',
                }
            )
            
            if created:
                user.set_password(data['password'])
                user.save()
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} resepsiyonist kullanıcı oluşturuldu'))

    def create_doctors(self, num_doctors):
        """Belirtilen sayıda doktor oluşturur."""
        created_count = 0
        for i in range(1, num_doctors + 1):
            first_name = self.get_random_first_name(gender='male' if i % 2 == 0 else 'female')
            last_name = self.get_random_last_name()
            specialization = random.choice(SPECIALIZATIONS)
            username = f"dr.{first_name.lower()}"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@meditrack.com',
                    'first_name': first_name,
                    'last_name': last_name,
                    'user_type': 'doctor',
                    'specialization': specialization,
                }
            )
            
            if created:
                user.set_password('doctor123')
                user.save()
                created_count += 1
        
        doctors = User.objects.filter(user_type='doctor')
        self.stdout.write(self.style.SUCCESS(f'{created_count} doktor kullanıcı oluşturuldu'))
        return doctors

    def create_patients(self, num_patients):
        """Belirtilen sayıda hasta oluşturur."""
        created_count = 0
        for i in range(1, num_patients + 1):
            first_name = self.get_random_first_name(gender='male' if i % 2 == 0 else 'female')
            last_name = self.get_random_last_name()
            username = f"hasta.{first_name.lower()}"
            
            # Rastgele adres oluştur
            location = random.choice(CITIES_AND_DISTRICTS)
            district = random.choice(location['districts'])
            address = f"{random.randint(1, 100)}. Sokak, No: {random.randint(1, 100)}, {district} / {location['city']}"
            
            # Rastgele doğum tarihi (18-80 yaş arası)
            age = random.randint(18, 80)
            birth_date = datetime.now().date() - timedelta(days=age*365)
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@gmail.com',
                    'first_name': first_name,
                    'last_name': last_name,
                    'user_type': 'patient',
                    'date_of_birth': birth_date,
                    'phone_number': f"05{random.randint(10, 99)}{random.randint(1000000, 9999999)}",
                    'address': address,
                    'blood_type': random.choice(BLOOD_TYPES),
                }
            )
            
            if created:
                user.set_password('patient123')
                user.save()
                created_count += 1
        
        patients = User.objects.filter(user_type='patient')
        self.stdout.write(self.style.SUCCESS(f'{created_count} hasta kullanıcı oluşturuldu'))
        return patients

    def create_appointments(self, num_appointments, doctors, patients):
        """Belirtilen sayıda randevu oluşturur."""
        if not doctors.exists() or not patients.exists():
            self.stdout.write(self.style.ERROR('Doktor veya hasta bulunamadı! Randevular oluşturulamıyor.'))
            return []
        
        # Randevu saatleri (09:00 - 17:00, 30 dakika aralıklarla)
        appointment_times = []
        start_time = time(9, 0)
        for i in range(16):  # 8 saat x 2 (30 dakikalık dilimler)
            hour = 9 + i // 2
            minute = 0 if i % 2 == 0 else 30
            appointment_times.append(time(hour, minute))
        
        # Son 60 gün ve gelecek 30 gün arasında randevular oluştur
        start_date = timezone.now().date() - timedelta(days=60)
        end_date = timezone.now().date() + timedelta(days=30)
        date_range = (end_date - start_date).days
        
        created_count = 0
        appointments = []
        
        for _ in range(num_appointments):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            
            # Rastgele tarih ve saat
            random_day = random.randint(0, date_range)
            appointment_date = start_date + timedelta(days=random_day)
            appointment_time = random.choice(appointment_times)
            
            # Randevu durumu
            if appointment_date < timezone.now().date():
                # Geçmiş randevular ya tamamlandı ya da iptal edildi
                status = random.choice(['completed', 'cancelled', 'completed', 'completed'])  # Daha fazla tamamlanmış
            else:
                # Gelecek randevular planlandı
                status = 'planned'
            
            # Rastgele açıklama
            descriptions = [
                'Genel kontrol',
                'Düzenli kontrol',
                'Ağrı şikayeti',
                'Takip randevusu',
                'İlaç yazımı',
                'Test sonuçlarının değerlendirilmesi',
                'Başağrısı şikayeti',
                'Sırt ağrısı',
                'Tansiyon kontrolü',
                'Mide şikayetleri'
            ]
            
            description = random.choice(descriptions)
            
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=appointment_date,
                time=appointment_time,
                description=description,
                status=status
            )
            
            appointments.append(appointment)
            created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} randevu oluşturuldu'))
        return appointments

    def create_treatments_and_prescriptions(self, num_treatments, appointments):
        """Belirtilen sayıda tedavi ve reçete oluşturur."""
        # Sadece tamamlanmış randevulara tedavi eklenebilir
        completed_appointments = [appt for appt in appointments if appt.status == 'completed']
        
        if not completed_appointments:
            self.stdout.write(self.style.ERROR('Tamamlanmış randevu bulunamadı! Tedaviler oluşturulamıyor.'))
            return []
        
        # Rastgele tedavi sayısı oluştur (num_treatments'dan fazla tamamlanmış randevu yoksa)
        treatment_count = min(len(completed_appointments), num_treatments)
        created_count = 0
        created_treatments = []
        
        for i in range(treatment_count):
            # Henüz tedavisi olmayan rastgele bir tamamlanmış randevu seç
            available_appointments = [appt for appt in completed_appointments if not hasattr(appt, 'treatment')]
            if not available_appointments:
                break
                
            appointment = random.choice(available_appointments)
            
            # Tedavi oluştur
            diagnosis = random.choice(DIAGNOSES)
            notes = random.choice([
                'Hasta bir hafta içinde iyileşme gösterdi.',
                'Tedaviye iyi yanıt verdi.',
                'Düzenli ilaç kullanımı önemli.',
                'Kontrol randevusu 2 hafta sonraya planlandı.',
                'Hasta bilgilendirildi.',
                None,  # Bazen not olmayabilir
            ])
            
            treatment = Treatment.objects.create(
                appointment=appointment,
                diagnosis=diagnosis,
                notes=notes
            )
            
            created_count += 1
            created_treatments.append(treatment)
            
            # 1-3 arası rastgele reçete ekle
            num_prescriptions = random.randint(1, 3)
            medication_options = random.sample(MEDICATIONS, num_prescriptions)
            
            for medication in medication_options:
                # Yeni ilaç nesnesi oluştur
                med_obj = Medication.objects.create(
                    name=medication['name'],
                    active_ingredient=f"Etken madde {random.randint(1, 100)}",
                    description=f"{medication['name']} - {medication['dosage']} dozunda",
                    side_effects="Uyku hali, baş dönmesi, mide bulantısı görülebilir."
                )
                
                # Reçete oluştur
                Prescription.objects.create(
                    treatment=treatment,
                    medication=med_obj,
                    name=medication['name'],
                    dosage=medication['dosage'],
                    instructions=medication['instructions']
                )
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} tedavi ve {created_count * 2} ortalama reçete oluşturuldu'))
        return created_treatments

    def create_doctor_availabilities(self, num_availabilities, doctors):
        """Doktorlar için uygunluk saatleri oluşturur."""
        if not doctors.exists():
            self.stdout.write(self.style.ERROR('Doktor bulunamadı! Uygunluklar oluşturulamıyor.'))
            return
        
        # Gün isimleri (0: Pazartesi, 6: Pazar)
        days = [0, 1, 2, 3, 4]  # Hafta içi günleri
        
        created_count = 0
        for doctor in doctors:
            if doctor.user_type != 'doctor':
                continue
                
            # Her doktor için 3-5 gün uygunluk ekle
            available_days = random.sample(days, random.randint(3, 5))
            
            for day in available_days:
                # Çalışma saatleri varyasyonları
                start_options = ['08:00', '09:00', '10:00']
                end_options = ['16:00', '17:00', '18:00']
                
                # Rastgele başlangıç ve bitiş saati seç
                start_time = random.choice(start_options)
                end_time = random.choice(end_options)
                
                # Tutarlılığı sağlamak için başlangıç ve bitiş saatlerini kontrol et
                start_hour = int(start_time.split(':')[0])
                end_hour = int(end_time.split(':')[0])
                
                if end_hour <= start_hour:
                    end_time = '18:00'  # Varsayılan bitiş saati
                
                try:
                    # Uygunluk oluştur
                    DoctorAvailability.objects.create(
                        doctor=doctor,
                        weekday=day,
                        start_time=start_time,
                        end_time=end_time
                    )
                    created_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Uygunluk oluşturulurken hata: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} doktor uygunluğu oluşturuldu'))

    def create_doctor_timeoffs(self, num_timeoffs, doctors):
        """Doktorlar için izin günleri oluşturur."""
        if not doctors.exists():
            self.stdout.write(self.style.ERROR('Doktor bulunamadı! İzinler oluşturulamıyor.'))
            return
        
        # İzin nedenleri
        reasons = ['Yıllık İzin', 'Hastalık İzni', 'Konferans', 'Eğitim', 'Kişisel İşler']
        
        created_count = 0
        today = timezone.now().date()
        
        for _ in range(num_timeoffs):
            try:
                # Doktor tipine sahip kullanıcılardan birini seç
                doctor_users = [d for d in doctors if d.user_type == 'doctor']
                if not doctor_users:
                    break
                    
                doctor = random.choice(doctor_users)
                
                # İzin türü
                reason = random.choice(reasons)
                
                # Rastgele tarih aralığı (geçmiş veya gelecek)
                if random.random() < 0.5:
                    # Geçmiş izin
                    start_date = today - timedelta(days=random.randint(60, 90))
                else:
                    # Gelecek izin
                    start_date = today + timedelta(days=random.randint(10, 60))
                
                # İzin süresi (1-7 gün)
                duration = random.randint(1, 7)
                end_date = start_date + timedelta(days=duration)
                
                # İzin oluştur
                DoctorTimeOff.objects.create(
                    doctor=doctor,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'İzin oluşturulurken hata: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} doktor izni oluşturuldu'))

    def create_medical_histories(self, num_medicalhistories, patients):
        """Hastalar için tıbbi geçmiş kayıtları oluşturur."""
        if not patients.exists():
            self.stdout.write(self.style.ERROR('Hasta bulunamadı! Tıbbi geçmiş oluşturulamıyor.'))
            return
        
        # Tıbbi durumlar
        conditions = [
            'Hipertansiyon', 'Diyabet', 'Astım', 'Kalp Hastalığı', 'Migren', 
            'Romatizma', 'Tiroid Hastalığı', 'Depresyon', 'Anksiyete Bozukluğu',
            'Kolesterol', 'Reflü', 'Ülser', 'Kronik Bronşit', 'Sedef Hastalığı',
            'Alerji', 'Artrit', 'Osteoporoz', 'Epilepsi', 'Anemi'
        ]
        
        # Durum türleri
        condition_types = ['chronic', 'surgery', 'allergy', 'medication', 'other']
        
        created_count = 0
        today = timezone.now().date()
        
        for _ in range(num_medicalhistories):
            try:
                # Hasta tipine sahip kullanıcılardan birini seç
                patient_users = [p for p in patients if p.user_type == 'patient']
                if not patient_users:
                    break
                    
                patient = random.choice(patient_users)
                
                # Rastgele bir durum seç
                condition = random.choice(conditions)
                condition_type = random.choice(condition_types)
                
                # Teşhis tarihi (1-15 yıl öncesi)
                years_ago = random.randint(1, 15)
                diagnosed_date = today - timedelta(days=years_ago * 365)
                
                # Notlar
                notes_options = [
                    f'{condition} teşhisi konuldu. Düzenli takip gerekli.',
                    f'{condition} için düzenli ilaç kullanımı önerildi.',
                    f'{condition} kontrol altında, 6 ayda bir kontrol önerisi.',
                    f'Aile geçmişinde de bulunan {condition} için yaşam tarzı değişiklikleri önerildi.',
                    f'{condition} durumu için hasta bilgilendirildi, düzenli kontroller planlandı.'
                ]
                
                # Tıbbi geçmiş oluştur
                MedicalHistory.objects.create(
                    patient=patient,
                    condition=condition,
                    condition_type=condition_type,
                    diagnosed_date=diagnosed_date,
                    notes=random.choice(notes_options)
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Tıbbi geçmiş oluşturulurken hata: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} tıbbi geçmiş kaydı oluşturuldu'))

    def create_lab_tests_and_results(self, doctors, patients):
        """Laboratuvar testleri ve sonuçları oluşturur."""
        if not doctors.exists() or not patients.exists():
            self.stdout.write(self.style.ERROR('Doktor veya hasta bulunamadı! Lab testleri oluşturulamıyor.'))
            return
        
        # Test türleri
        test_types = [
            'Tam Kan Sayımı', 'Kan Şekeri', 'Kolesterol Paneli', 'Karaciğer Fonksiyon Testi',
            'Böbrek Fonksiyon Testi', 'Tiroid Paneli', 'İdrar Tahlili', 'HbA1c',
            'Vitamin D', 'Vitamin B12', 'Demir', 'Elektrolit Paneli'
        ]
        
        created_tests_count = 0
        created_results_count = 0
        today = timezone.now().date()
        
        # Doktor ve hasta listelerini filtrele
        doctor_users = [d for d in doctors if d.user_type == 'doctor']
        patient_users = [p for p in patients if p.user_type == 'patient']
        
        if not doctor_users or not patient_users:
            self.stdout.write(self.style.ERROR('Doktor veya hasta bulunamadı! Lab testleri oluşturulamıyor.'))
            return
        
        # 20-30 arası test oluştur
        num_tests = random.randint(20, 30)
        
        for _ in range(num_tests):
            try:
                # Rastgele hasta ve doktor seç
                patient = random.choice(patient_users)
                doctor = random.choice(doctor_users)
                
                # Test türü
                test_type = random.choice(test_types)
                
                # Test tarihi (son 180 gün içinde)
                days_ago = random.randint(1, 180)
                test_date = today - timedelta(days=days_ago)
                
                # Test durumu
                if days_ago > 7:
                    status = 'completed'  # 1 haftadan eski testler tamamlandı
                else:
                    status = random.choice(['pending', 'completed', 'completed'])  # Yeni testler çoğunlukla tamamlandı
                
                # Lab testi oluştur
                lab_test = LabTest.objects.create(
                    patient=patient,
                    doctor=doctor,
                    test_type=test_type,
                    test_date=test_date,
                    status=status
                )
                created_tests_count += 1
                
                # Tamamlanan testler için sonuç oluştur
                if status == 'completed':
                    # Sonuç tarihi (test tarihinden 1-3 gün sonra)
                    result_date = test_date + timedelta(days=random.randint(1, 3))
                    
                    # Sonuçlar ve yorumlar
                    results_options = [
                        f'{test_type} sonuçları normal aralıkta.',
                        f'{test_type} sonuçlarında hafif anormallikler görüldü.',
                        f'{test_type} değerleri referans aralığında.',
                        f'{test_type} sonuçları detaylı olarak incelendi.'
                    ]
                    
                    interpretation_options = [
                        'Normal sonuçlar, klinik bulgular ile uyumlu.',
                        'Hafif anormallikler mevcut, klinik açıdan anlamlı değil.',
                        'Sonuçlar değerlendirildi, tedavi değişikliği gerektirmiyor.',
                        'Sonuçlar normal aralıkta, sağlık durumu iyi.'
                    ]
                    
                    recommendations_options = [
                        'Kontrol gerektirmiyor.',
                        '6 ay sonra kontrol önerilir.',
                        'Mevcut tedaviye devam edilmesi uygun.',
                        'Yaşam tarzı değişiklikleri önerilir.',
                        'Yıllık rutin kontroller yeterli.'
                    ]
                    
                    # Sonuç oluştur
                    TestResult.objects.create(
                        lab_test=lab_test,
                        result_date=result_date,
                        results=random.choice(results_options),
                        interpretation=random.choice(interpretation_options),
                        recommendations=random.choice(recommendations_options)
                    )
                    created_results_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Lab testi/sonucu oluşturulurken hata: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_tests_count} lab testi ve {created_results_count} lab sonucu oluşturuldu'))

    def create_imaging_and_results(self, doctors, patients):
        """Tıbbi görüntüler ve raporlar oluşturur."""
        if not doctors.exists() or not patients.exists():
            self.stdout.write(self.style.ERROR('Doktor veya hasta bulunamadı! Tıbbi görüntüler oluşturulamıyor.'))
            return
        
        # Görüntüleme türleri
        image_types = ['xray', 'mri', 'ct', 'ultrasound', 'other']
        
        # Vücut bölgeleri
        body_parts = [
            'Göğüs', 'Abdomen', 'Kafa', 'Omurga', 'Pelvis', 
            'Diz', 'Omuz', 'El Bileği', 'Ayak Bileği', 'Kalça'
        ]
        
        created_images_count = 0
        created_reports_count = 0
        today = timezone.now().date()
        
        # Doktor ve hasta listelerini filtrele
        doctor_users = [d for d in doctors if d.user_type == 'doctor']
        patient_users = [p for p in patients if p.user_type == 'patient']
        
        if not doctor_users or not patient_users:
            self.stdout.write(self.style.ERROR('Doktor veya hasta bulunamadı! Tıbbi görüntüler oluşturulamıyor.'))
            return
        
        # Rastgele tedaviler oluştur (sonradan kullanılacak)
        treatments = []
        for _ in range(20):
            # Rastgele bir randevu oluştur
            patient = random.choice(patient_users)
            doctor = random.choice(doctor_users)
            
            # Randevu tarihi
            appointment_date = today - timedelta(days=random.randint(10, 60))
            appointment_time = time(random.randint(9, 16), random.choice([0, 15, 30, 45]))
            
            # Randevu oluştur
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=appointment_date,
                time=appointment_time,
                description="Görüntüleme için randevu",
                status="completed"
            )
            
            # Tedavi oluştur
            treatment = Treatment.objects.create(
                appointment=appointment,
                diagnosis="Görüntüleme gerekli durum",
                notes="Görüntüleme sonucuna göre tedavi planlanacak"
            )
            treatments.append(treatment)
        
        # 15-25 arası görüntüleme oluştur
        num_imaging = random.randint(15, 25)
        
        for _ in range(num_imaging):
            try:
                # Rastgele tedavi, hasta ve doktor seç
                treatment = random.choice(treatments)
                patient = treatment.patient
                doctor = treatment.doctor
                
                # Görüntüleme türü ve vücut bölgesi
                image_type = random.choice(image_types)
                body_part = random.choice(body_parts)
                
                # Görüntüleme tarihi (son 60 gün içinde)
                days_ago = random.randint(1, 60)
                taken_date = today - timedelta(days=days_ago)
                
                # Açıklama
                description_options = [
                    f'{body_part} ağrısı nedeniyle {image_type} görüntüleme',
                    f'{body_part} bölgesinde şişlik nedeniyle görüntüleme',
                    f'{body_part} bölgesinde travma sonrası kontrol',
                    f'{body_part} bölgesinde anormallik şüphesi',
                    'Rutin kontrol',
                    'Takip görüntülemesi'
                ]
                
                # Tıbbi görüntü oluştur
                image = MedicalImage.objects.create(
                    treatment=treatment,
                    patient=patient,
                    doctor=doctor,
                    image_type=image_type,
                    body_part=body_part,
                    taken_date=taken_date,
                    description=random.choice(description_options),
                    image_file="medical_images/sample.jpg"  # Örnek dosya adı
                )
                created_images_count += 1
                
                # Rastgele görüntüler için rapor oluştur (%70 olasılıkla)
                if random.random() < 0.7:
                    # Rapor tarihi (görüntüleme tarihinden 1-3 gün sonra)
                    report_date = taken_date + timedelta(days=random.randint(1, 3))
                    
                    # Rapor içerikleri
                    title_options = [
                        f'{body_part} {image_type} Değerlendirmesi',
                        f'{body_part} Görüntüleme Raporu',
                        f'{image_type.upper()} Raporu - {body_part}',
                        f'Tıbbi Değerlendirme - {body_part}'
                    ]
                    
                    content_options = [
                        f'{body_part} bölgesinde herhangi bir anormallik saptanmadı. Normal anatomik yapı ve görünüm mevcuttur.',
                        f'{body_part} bölgesinde minimal dejeneratif değişiklikler gözlenmiştir. Klinik açıdan anlamlı patoloji izlenmemiştir.',
                        f'{body_part} görüntülemesi normal sınırlarda olup, hasta şikayetlerini açıklayacak bir bulgu saptanmamıştır.',
                        f'{body_part} bölgesinde hafif değişiklikler mevcut olup, klinik korelasyon önerilir. Kontrol görüntüleme gerekli değildir.'
                    ]
                    
                    # Rapor oluştur
                    Report.objects.create(
                        treatment=treatment,
                        patient=patient,
                        doctor=doctor,
                        report_type='diagnostic',
                        title=random.choice(title_options),
                        content=random.choice(content_options),
                        valid_from=report_date,
                        valid_until=report_date + timedelta(days=365)  # 1 yıl geçerli
                    )
                    created_reports_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Tıbbi görüntü/rapor oluşturulurken hata: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_images_count} tıbbi görüntü ve {created_reports_count} rapor oluşturuldu'))

    def create_notifications(self, num_notifications):
        """Kullanıcılar için bildirimler oluşturur."""
        all_users = User.objects.all()
        
        if not all_users.exists():
            self.stdout.write(self.style.ERROR('Kullanıcı bulunamadı! Bildirimler oluşturulamıyor.'))
            return
        
        # Bildirim türleri
        notification_types = [
            'appointment_reminder', 'prescription_refill', 'test_result',
            'message', 'system'
        ]
        
        created_count = 0
        today = timezone.now()
        
        for _ in range(num_notifications):
            try:
                # Rastgele bir kullanıcı seç
                user = random.choice(all_users)
                
                # Bildirim türü
                notification_type = random.choice(notification_types)
                
                # Bildirim içeriği
                content = ''
                if notification_type == 'appointment_reminder':
                    content = random.choice([
                        "Yaklaşan randevunuz hakkında hatırlatma.",
                        "Yarınki randevunuzu unutmayın.",
                        "Önümüzdeki hafta için planlanmış randevunuz var.",
                        "Dr. ile randevunuz 3 gün sonra."
                    ])
                elif notification_type == 'prescription_refill':
                    content = random.choice([
                        "Reçeteniz yenileme zamanı geldi.",
                        "İlaçlarınız bitmek üzere, lütfen doktorunuzla iletişime geçin.",
                        "Reçeteniz hazır, eczaneden alabilirsiniz.",
                        "İlaç tedaviniz için yenileme hatırlatması."
                    ])
                elif notification_type == 'test_result':
                    content = random.choice([
                        "Test sonuçlarınız hazır.",
                        "Laboratuvar sonuçlarınız sisteme yüklendi.",
                        "Görüntüleme sonuçlarınız doktorunuz tarafından değerlendirildi.",
                        "Yeni test sonuçlarınız mevcut."
                    ])
                elif notification_type == 'message':
                    content = random.choice([
                        "Doktorunuzdan yeni bir mesaj aldınız.",
                        "Sağlık ekibinizden mesaj var.",
                        "Tedaviniz hakkında yeni bir mesaj.",
                        "Randevunuz hakkında mesaj aldınız."
                    ])
                else:  # system
                    content = random.choice([
                        "Sistem bakımı nedeniyle kısa süreli kesinti olacaktır.",
                        "Uygulama güncellemesi yapıldı.",
                        "Hesap bilgilerinizi güncelleyin.",
                        "Yeni özellikler eklendi, keşfedin!"
                    ])
                
                # Oluşturulma tarihi (son 30 gün içinde)
                days_ago = random.randint(0, 30)
                created_at = today - timedelta(days=days_ago)
                
                # Okunma durumu
                is_read = random.choice([True, False]) if days_ago > 2 else False
                
                # Bildirim oluştur
                Notification.objects.create(
                    user=user,
                    notification_type=notification_type,
                    content=content,
                    is_read=is_read,
                    created_at=created_at
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Bildirim oluşturulurken hata: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} bildirim oluşturuldu'))

    def get_random_first_name(self, gender='male'):
        """Rastgele Türkçe isim döndürür."""
        male_names = ['Ahmet', 'Mehmet', 'Mustafa', 'Ali', 'Hasan', 'Hüseyin', 'İbrahim', 'Osman', 'Yusuf', 'Murat',
                     'Ömer', 'Enes', 'Emre', 'Baran', 'Can', 'Deniz', 'Eren', 'Furkan', 'Gökhan', 'Kemal']
        female_names = ['Ayşe', 'Fatma', 'Emine', 'Hatice', 'Zeynep', 'Elif', 'Meryem', 'Esra', 'Nur', 'Zehra',
                       'Melek', 'Ebru', 'Derya', 'Canan', 'Büşra', 'Aslı', 'Gül', 'Seda', 'Pınar', 'Özge']
        
        if gender == 'male':
            return random.choice(male_names)
        else:
            return random.choice(female_names)

    def get_random_last_name(self):
        """Rastgele Türkçe soyadı döndürür."""
        last_names = ['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Yıldız', 'Yıldırım', 'Öztürk', 'Aydın', 'Özdemir',
                     'Arslan', 'Doğan', 'Kılıç', 'Aslan', 'Çetin', 'Kara', 'Koç', 'Kurt', 'Özkan', 'Şimşek']
        return random.choice(last_names)