#!/usr/bin/env python
"""
Test script for new two-factor password reset system
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from users.models import PasswordResetVerification, PasswordResetToken, UserProfile

User = get_user_model()

def test_new_password_reset_system():
    print("Testing new two-factor password reset system...")
    
    # Create a test user if not exists
    user, created = User.objects.get_or_create(
        username='testuser_reset',
        defaults={
            'email': 'test_reset@example.com',
            'password': 'testpass123'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    
    # Create or update user profile with phone and telegram chat ID
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.phone = '+79123456788'  # Unique phone number
    profile.telegram_chat_id = '987654321'  # Unique mock chat ID
    profile.save()
    print(f"Updated profile for {user.username}")
    
    # Test password reset request
    client = Client()
    
    try:
        response = client.post('/accounts/password-reset/', {
            'phone': '+79123456788'  # Use the same phone number
        })
        print(f"Password reset request status: {response.status_code}")
        
        # Check if verification was created
        verification = PasswordResetVerification.objects.filter(
            user=user, 
            verified_at__isnull=True
        ).first()
        
        if verification:
            print(f"✅ Verification code created: {verification.verification_code}")
            print(f"✅ Verification expires at: {verification.expires_at}")
            print(f"✅ Failed attempts: {verification.failed_attempts}")
            print(f"✅ Can attempt: {verification.can_attempt}")
            
            # Test Telegram bot verification simulation
            print("\n--- Simulating Telegram Bot Verification ---")
            
            # Test 1: Correct verification
            print(f"Testing correct code: {verification.verification_code}")
            # Simulate the verification logic
            test_verification = PasswordResetVerification.objects.filter(
                verification_code=verification.verification_code.upper(),
                verified_at__isnull=True
            ).select_related('user').first()
            
            if test_verification:
                print(f"✅ Found verification object")
                print(f"✅ User: {test_verification.user.username}")
                
                # Check chat_id match
                user_profile = test_verification.user.profile
                if user_profile.telegram_chat_id == '987654321':
                    print("✅ Chat ID matches")
                    
                    # Create reset token
                    reset_token = PasswordResetToken.objects.create(user=test_verification.user)
                    print(f"✅ Reset token created: {reset_token.token}")
                    
                    # Mark verification as successful
                    test_verification.mark_verified(reset_token.token)
                    print("✅ Verification marked as successful")
                    
                    # Create reset URL
                    reset_url = f"http://127.0.0.1:8000/accounts/password-reset/confirm/{reset_token.token}/"
                    print(f"✅ Reset URL: {reset_url}")
                    
                else:
                    print("❌ Chat ID doesn't match")
            else:
                print("❌ Verification not found")
                
        else:
            print("❌ No verification object created")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_new_password_reset_system()
