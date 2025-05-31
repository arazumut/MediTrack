# MediTrack - Klinik Hasta Takip ve Randevu Sistemi

MediTrack, sağlık merkezleri için tasarlanmış kapsamlı bir hasta takip ve randevu yönetim sistemidir. Bu sistem, hasta kayıtları, randevu planlaması, tedavi geçmişi ve reçete yönetimi gibi temel klinik işlevlerini içerir.

## Özellikler

- **Kullanıcı ve Rol Yönetimi**: Hasta, doktor, resepsiyonist ve admin rolleri
- **Hasta Yönetimi**: Hasta kaydı, profil bilgileri düzenleme, tedavi geçmişi görüntüleme
- **Randevu Sistemi**: Randevu oluşturma, güncelleme, iptal etme ve görüntüleme
- **Tedavi ve Reçete Yönetimi**: Tedavi notları, teşhis, reçete önerisi ekleme
- **Bildirim Sistemi**: Randevu hatırlatmaları (e-posta ile)
- **Kapsamlı Yetkilendirme**: Her kullanıcı rolü için özel izinler ve sınırlamalar

## Kurulum

1. Python 3.8+ kurulu olduğundan emin olun
2. Bu projeyi klonlayın
3. Sanal ortam oluşturun:
   ```
   python -m venv venv
   ```
4. Sanal ortamı aktifleştirin:
   - Windows: `venv\Scripts\activate`
   - Unix/Mac: `source venv/bin/activate`
5. Bağımlılıkları yükleyin:
   ```
   pip install -r requirements.txt
   ```
6. Veritabanı migrasyonlarını gerçekleştirin:
   ```
   python manage.py migrate
   ```
7. Örnek verileri ve admin kullanıcısını yükleyin:
   ```
   python manage.py loaddata initial_data
   ```
8. Sunucuyu başlatın:
   ```
   python manage.py runserver
   ```

## Örnek Kullanıcılar

Aşağıdaki örnek kullanıcılar, sistemi test etmek için kullanılabilir:

| Kullanıcı Adı | Şifre | Rol |
|---------------|-------|-----|
| admin | admin123 | Admin |
| doktor1 | doktor123 | Doktor |
| doktor2 | doktor123 | Doktor |
| resepsiyon1 | resepsiyon123 | Resepsiyonist |
| hasta1 | hasta123 | Hasta |
| hasta2 | hasta123 | Hasta |

## Kullanıcı Rolleri ve İzinleri

| Rol | İzinler |
|-----|---------|
| Hasta | - Kendi randevularını görüntüleyebilir<br>- Kendi tedavi geçmişini görüntüleyebilir<br>- Kendi profilini güncelleyebilir |
| Doktor | - Kendi randevularını görüntüleyebilir<br>- Hastalarına tedavi ve reçete ekleyebilir<br>- Hastaları hakkında bilgi görüntüleyebilir |
| Resepsiyonist | - Hasta kaydı oluşturabilir<br>- Randevu oluşturabilir, güncelleyebilir<br>- Tüm hastaları ve randevuları görüntüleyebilir |
| Admin | - Tam sistem erişimi<br>- Tüm kullanıcıları yönetebilir<br>- Tüm verileri görüntüleyebilir ve düzenleyebilir |

## Teknolojiler

- Django 5.2
- SQLite (Geliştirme için)
- Bootstrap 5
- JavaScript

## Ekran Görüntüleri

*Ekran görüntüleri gelecek*

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Sorularınız veya geri bildirimleriniz için lütfen iletişime geçin.

---

Geliştirici: [İsim] 