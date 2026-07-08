#!/usr/bin/env python
"""
Test script for password reset functionality
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory, Client
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from users.views import password_reset_request
from users.models import PasswordResetToken, UserProfile

User = get_user_model()

def get_request_with_middleware(path, data=None):
    """Create a request with proper middleware setup"""
    factory = RequestFactory()
    if data:
        request = factory.post(path, data)
    else:
        request = factory.get(path)
    
    # Add session middleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # Add message middleware
    middleware = MessageMiddleware(lambda x: None)
    middleware.process_request(request)
    request.messages = FallbackStorage(request)
    
    # Set proper host
    request.META['HTTP_HOST'] = '127.0.0.1:8000'
    request.META['SERVER_NAME'] = '127.0.0.1'
    request.META['SERVER_PORT'] = '8000'
    
    return request

def test_password_reset():
    print("Testing password reset functionality...")
    
    # Create a test user if not exists
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    
    # Create or update user profile with phone and telegram chat ID
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.phone = '+79123456789'
    profile.telegram_chat_id = '123456789'  # Mock chat ID
    profile.save()
    print(f"Updated profile for {user.username}")
    
    # Test with client (better simulation)
    client = Client()
    
    try:
        response = client.post('/accounts/password-reset/', {
            'phone': '+79123456789'
        })
        print(f"Response status: {response.status_code}")
        
        # Check if token was created
        token = PasswordResetToken.objects.filter(user=user, used_at__isnull=True).first()
        if token:
            print(f"✅ Token created: {token.token}")
            print(f"✅ Token expires at: {token.expires_at}")
            print(f"✅ Reset URL would be: http://127.0.0.1:8000/accounts/password-reset/confirm/{token.token}/")
        else:
            print("❌ No token was created")
            
    except Exception as e:
        print(f"❌ Error during password reset request: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_password_reset()
