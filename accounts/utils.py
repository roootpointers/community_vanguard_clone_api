import uuid
import random
import string
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_username(email, first_name=None, last_name=None):
    """
    Generate a unique username based on email, first name, and last name.
    Falls back to email if other options fail.
    """
    # Try email-based username first
    base_username = email.split('@')[0]
    
    # Clean the username to only contain valid characters
    base_username = ''.join(c for c in base_username if c.isalnum() or c in '_')
    
    if not User.objects.filter(username=base_username).exists():
        return base_username
    
    # If email-based username exists, try with first and last name
    if first_name and last_name:
        name_username = f"{first_name.lower()}.{last_name.lower()}"
        name_username = ''.join(c for c in name_username if c.isalnum() or c in '_.')
        
        if not User.objects.filter(username=name_username).exists():
            return name_username
    
    # If both fail, append random string to base username
    while True:
        random_suffix = ''.join(random.choices(string.digits, k=4))
        username = f"{base_username}_{random_suffix}"
        
        if not User.objects.filter(username=username).exists():
            return username


def generate_username_from_email(email):
    """
    Simple username generator that uses email as base.
    This is the fallback method.
    """
    return email.split('@')[0] + '_' + str(uuid.uuid4())[:8]