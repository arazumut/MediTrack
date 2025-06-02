from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse

from core.models_communication import Notification
from appointments.models_availability import DoctorAvailability, DoctorTimeOff
from users.models import User


def create_notification(user, notification_type, title, message, related_url=None):
    """
    Kullanıcı için bildirim oluşturan yardımcı fonksiyon.
    
    Args:
        user: Kullanıcı nesnesi (User)
        notification_type: Bildirim tipi (choices'dan biri)
        title: Bildirim başlığı
        message: Bildirim mesajı
        related_url: İlgili URL (isteğe bağlı)
    
    Returns:
        Oluşturulan bildirim nesnesi
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_url=related_url
    )
    
    return notification


def create_availability_change_notification(doctor, operation_type, day=None, start_time=None, end_time=None):
    """
    Doktor uygunluk değişikliği için hastalarına bildirim gönderen fonksiyon.
    
    Args:
        doctor: Doktor nesnesi (User)
        operation_type: İşlem tipi ('added', 'updated', 'deleted')
        day: Değişiklik yapılan gün (isteğe bağlı)
        start_time: Başlangıç saati (isteğe bağlı)
        end_time: Bitiş saati (isteğe bağlı)
    """
    # Doktorun hastalarını bul (doktorla randevusu olan benzersiz hastalar)
    patients = User.objects.filter(
        user_type='patient',
        patient_appointments__doctor=doctor
    ).distinct()
    
    # İşlem tipine göre bildirim başlığı ve mesajı oluştur
    if operation_type == 'added':
        title = f"Dr. {doctor.get_full_name()} yeni çalışma saatleri ekledi"
        if day is not None and start_time is not None and end_time is not None:
            day_name = DoctorAvailability.WEEKDAY_CHOICES[day][1]
            message = f"Dr. {doctor.get_full_name()}, {day_name} günleri için {start_time} - {end_time} saatleri arasında yeni çalışma saati ekledi."
        else:
            message = f"Dr. {doctor.get_full_name()} çalışma saatlerini güncelledi. Randevu almak için doktor takvimini kontrol ediniz."
    
    elif operation_type == 'updated':
        title = f"Dr. {doctor.get_full_name()} çalışma saatlerini güncelledi"
        if day is not None and start_time is not None and end_time is not None:
            day_name = DoctorAvailability.WEEKDAY_CHOICES[day][1]
            message = f"Dr. {doctor.get_full_name()}, {day_name} günleri için çalışma saatlerini {start_time} - {end_time} olarak güncelledi."
        else:
            message = f"Dr. {doctor.get_full_name()} çalışma saatlerini güncelledi. Randevu almak için doktor takvimini kontrol ediniz."
    
    elif operation_type == 'deleted':
        title = f"Dr. {doctor.get_full_name()} bazı çalışma saatleri kaldırıldı"
        if day is not None:
            day_name = DoctorAvailability.WEEKDAY_CHOICES[day][1]
            message = f"Dr. {doctor.get_full_name()}, {day_name} günü için bazı çalışma saatleri kaldırıldı. Randevu almak için doktor takvimini kontrol ediniz."
        else:
            message = f"Dr. {doctor.get_full_name()} çalışma saatlerinde değişiklik yapıldı. Randevu almak için doktor takvimini kontrol ediniz."
    
    else:  # İzin ekleme/güncelleme/silme
        title = f"Dr. {doctor.get_full_name()} izin durumunda değişiklik"
        message = f"Dr. {doctor.get_full_name()}'in izin durumunda değişiklik oldu. Randevu almak için doktor takvimini kontrol ediniz."
    
    # İlgili URL oluştur (doktor takvimi)
    related_url = reverse('doctor-calendar', kwargs={'doctor_id': doctor.id})
    
    # Her hasta için bildirim oluştur
    for patient in patients:
        create_notification(
            user=patient,
            notification_type='system',
            title=title,
            message=message,
            related_url=related_url
        )


# Signal alıcıları
@receiver(post_save, sender=DoctorAvailability)
def doctor_availability_changed(sender, instance, created, **kwargs):
    """DoctorAvailability modelinde değişiklik olduğunda çalışan sinyal alıcısı"""
    if created:
        # Yeni bir çalışma saati eklendiğinde
        create_availability_change_notification(
            doctor=instance.doctor,
            operation_type='added',
            day=instance.weekday,
            start_time=instance.start_time,
            end_time=instance.end_time
        )
    else:
        # Mevcut bir çalışma saati güncellendiğinde
        create_availability_change_notification(
            doctor=instance.doctor,
            operation_type='updated', 
            day=instance.weekday,
            start_time=instance.start_time,
            end_time=instance.end_time
        )


@receiver(post_delete, sender=DoctorAvailability)
def doctor_availability_deleted(sender, instance, **kwargs):
    """DoctorAvailability modeli silindiğinde çalışan sinyal alıcısı"""
    create_availability_change_notification(
        doctor=instance.doctor,
        operation_type='deleted',
        day=instance.weekday
    )


@receiver(post_save, sender=DoctorTimeOff)
def doctor_timeoff_changed(sender, instance, created, **kwargs):
    """DoctorTimeOff modelinde değişiklik olduğunda çalışan sinyal alıcısı"""
    create_availability_change_notification(
        doctor=instance.doctor,
        operation_type='timeoff'
    )


@receiver(post_delete, sender=DoctorTimeOff)
def doctor_timeoff_deleted(sender, instance, **kwargs):
    """DoctorTimeOff modeli silindiğinde çalışan sinyal alıcısı"""
    create_availability_change_notification(
        doctor=instance.doctor, 
        operation_type='timeoff'
    )
