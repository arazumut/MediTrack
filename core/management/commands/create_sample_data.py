import random
from datetime import datetime, timedelta, time
import pytz
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from treatments.models import Treatment, Prescription

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
        
        # Randevular oluştur
        num_appointments = options['appointments']
        appointments = self.create_appointments(num_appointments, doctors, patients)
        
        # Tedaviler ve reçeteler oluştur
        num_treatments = options['treatments']
        self.create_treatments_and_prescriptions(num_treatments, appointments)
        
        self.stdout.write(self.style.SUCCESS('Örnek veriler başarıyla oluşturuldu!'))
        self.stdout.write(f'- {num_doctors} doktor')
        self.stdout.write(f'- {num_patients} hasta')
        self.stdout.write(f'- {num_appointments} randevu')
        self.stdout.write(f'- {num_treatments} tedavi ve reçete')

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
            return
        
        # Rastgele tedavi sayısı oluştur (num_treatments'dan fazla tamamlanmış randevu yoksa)
        treatment_count = min(len(completed_appointments), num_treatments)
        created_count = 0
        
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
            
            # 1-3 arası rastgele reçete ekle
            num_prescriptions = random.randint(1, 3)
            medication_options = random.sample(MEDICATIONS, num_prescriptions)
            
            for medication in medication_options:
                Prescription.objects.create(
                    treatment=treatment,
                    name=medication['name'],
                    dosage=medication['dosage'],
                    instructions=medication['instructions']
                )
            
            created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} tedavi ve {created_count * 2} ortalama reçete oluşturuldu'))

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