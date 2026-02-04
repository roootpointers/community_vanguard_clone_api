from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'
    verbose_name = 'Notifications'

    def ready(self):
        """
        Initialize Firebase when the app is ready
        """
        from .firebase_config import initialize_firebase
        initialize_firebase()
