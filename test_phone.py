#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from users.forms import UserProfileForm
from users.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='Admin_D')
profile = user.profile

print(f"Testing form for user: {user.username}")
print(f"Current phone: {profile.phone}")

# Test 1: Save new phone number
print("\n=== Test 1: Save new phone number ===")
form = UserProfileForm(data={'phone': '+79123456789'}, instance=profile)
print(f'Form valid: {form.is_valid()}')
if not form.is_valid():
    print(f'Errors: {form.errors}')
else:
    form.save()
    profile.refresh_from_db()
    print(f'Phone saved: {profile.phone}')

# Test 2: Update phone number
print("\n=== Test 2: Update phone number ===")
form2 = UserProfileForm(data={'phone': '89876543210'}, instance=profile)
print(f'Form valid: {form2.is_valid()}')
if not form2.is_valid():
    print(f'Errors: {form2.errors}')
else:
    form2.save()
    profile.refresh_from_db()
    print(f'Phone updated: {profile.phone}')

print("\n=== Tests completed ===")
