#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.forms import _normalize_ru_phone

User = get_user_model()

print("=== Тест нормализации телефона ===")
test_phones = ["+79151385478", "89151385478", "9151385478"]
for phone in test_phones:
    normalized = _normalize_ru_phone(phone)
    print(f"{phone} -> {normalized}")

print("\n=== Поиск пользователей по телефону ===")
phone = "+79151385478"
normalized_phone = _normalize_ru_phone(phone)
print(f"Ищем по нормализованному телефону: {normalized_phone}")

users = User.objects.filter(profile__phone__iexact=normalized_phone, is_active=True)
print(f"Найдено пользователей: {users.count()}")

for user in users:
    print(f"- {user.username}")
    print(f"  Телефон: {user.profile.phone}")
    print(f"  Telegram chat_id: {user.profile.telegram_chat_id}")
    print(f"  Email: {user.email}")
