import random
import threading
from accounts.models.user import User
from accounts.models.verification import UserOTP
from django.conf import settings
import re
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail
from django.core.mail.backends.smtp import EmailBackend
import string
import base64
from django.core.files.base import ContentFile
from typing import Any, Optional, Type
from rest_framework import pagination, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import math

PAGINATION_ITEM_PER_PAGE = 20

class CommonPagination(PageNumberPagination):
    page_size = PAGINATION_ITEM_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 500


class EmailService:
    """
    Service class for handling verification emails.
    This class provides methods for sending emails with proper configuration.
    """
    
    @staticmethod
    def send_email(recipient_email, subject, template_name, context):
        """
        Send an email using Django's built-in EmailMessage with proper SMTP authentication.
        
        Args:
            recipient_email (str): The recipient's email address
            subject (str): The email subject
            template_name (str): The name of the template to render
            context (dict): Context data for the template
            
        Returns:
            bool: True if successful, Exception object if failed
        """
        try:
            html_message = render_to_string(template_name, context)
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [recipient_email]
            
            # Create a custom email backend with authentication
            backend = EmailBackend(
                host=settings.EMAIL_HOST, 
                port=settings.EMAIL_PORT,
                username=from_email,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
            )
            
            # Create and send email with custom backend
            msg = EmailMessage(
                subject=subject, 
                body=html_message, 
                from_email=from_email, 
                to=recipient_list,
                connection=backend
            )
            msg.content_subtype = "html"
            msg.send()
            return True
        except Exception as e:
            return e
    
    @staticmethod
    def send_email_async(recipient_email, subject, template_name, context):
        """Send email asynchronously in a separate thread"""
        thread = threading.Thread(
            target=EmailService._send_email_thread, 
            args=(recipient_email, subject, template_name, context)
        )
        thread.start()
    
    @staticmethod
    def _send_email_thread(recipient_email, subject, template_name, context):
        """
        Helper method for sending email in a thread.
        
        Args:
            recipient_email (str): The recipient's email address
            subject (str): The email subject
            template_name (str): The name of the template to render
            context (dict): Context data for the template
        """
        EmailService.send_email(recipient_email, subject, template_name, context)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False


def send_verification_email(email, subject):
    """
    Generates an OTP, saves it to the database, and sends it to the user's email.
    
    Args:
        email (str): The recipient's email address
        subject (str): The email subject
        
    Returns:
        bool: True if successful, Exception object if failed
    """
    try:
        if is_valid_email(email):
            # Generate a unique OTP
            while True:
                otp = random.randint(100000, 999999)
                if not UserOTP.objects.filter(email=email, otp=otp).exists():
                    break
                    
            # Save OTP to database
            user_otp = UserOTP.objects.create(email=email, otp=otp)
            
            # Prepare context for email template
            context = {'otp': user_otp.otp}
            
            # Send email asynchronously for better performance
            EmailService.send_email_async(
                recipient_email=email,
                subject=subject,
                template_name='verification_template.html',
                context=context
            )
            return True
    except Exception as e:
        return e
