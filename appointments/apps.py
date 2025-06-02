from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointments'
    
    def ready(self):
        """
        Uygulama başlatıldığında sinyal alıcılarını kaydet
        """
        import core.utils  # noqa
