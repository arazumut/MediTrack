from django.core.management.base import BaseCommand
from django.utils import timezone
from core.utils import get_upcoming_appointments, send_appointment_reminder_email
from core.models_communication import CommunicationNotification

class Command(BaseCommand):
    help = 'Yaklaşan randevular için hatırlatma e-postaları ve bildirimleri gönderir'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Kaç gün sonraki randevular için hatırlatma gönderilecek (varsayılan: 1)'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Yaklaşan randevuları al
        appointments = get_upcoming_appointments(days=days)
        
        self.stdout.write(f"{len(appointments)} adet yaklaşan randevu bulundu.")
        
        # Her randevu için hatırlatma gönder
        for appointment in appointments:
            # E-posta gönder
            try:
                send_appointment_reminder_email(appointment)
                self.stdout.write(self.style.SUCCESS(
                    f"E-posta gönderildi: {appointment.patient.email} - {appointment.date}"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"E-posta gönderilemedi: {appointment.patient.email} - Hata: {str(e)}"
                ))
            
            # Bildirim oluştur
            try:
                CommunicationNotification.objects.create(
                    user=appointment.patient,
                    title=f"Randevu Hatırlatması: {appointment.date.strftime('%d.%m.%Y')}",
                    message=f"Yarın saat {appointment.time.strftime('%H:%M')} için Dr. {appointment.doctor.get_full_name()} ile randevunuz bulunmaktadır.",
                    related_url=f"/appointments/{appointment.id}/",
                    notification_type="appointment_reminder"
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Bildirim oluşturuldu: {appointment.patient.get_full_name()}"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Bildirim oluşturulamadı: {appointment.patient.get_full_name()} - Hata: {str(e)}"
                ))
        
        self.stdout.write(self.style.SUCCESS(f"Toplam {len(appointments)} adet hatırlatma gönderildi.")) 