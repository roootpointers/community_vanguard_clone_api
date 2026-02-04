import firebase_admin
from firebase_admin import credentials
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initialize Firebase Admin SDK
    """
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
        logger.info("Firebase Admin SDK already initialized")
        return True
    except ValueError:
        # Firebase not initialized, initialize it
        try:
            # Path to service account key
            service_account_path = settings.FCM_DJANGO_SETTINGS.get('FCM_SERVICE_ACCOUNT_KEY_PATH')
            
            if not service_account_path or not os.path.exists(service_account_path):
                logger.error(f"Firebase service account key not found at: {service_account_path}")
                return False
            
            # Initialize Firebase
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            
            logger.info("Firebase Admin SDK initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            return False
