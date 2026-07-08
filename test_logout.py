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

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== Тест Logout функциональности ===")

# Создаем тестовый клиент
client = Client()

# Проверяем URL logout
print("Проверяем URL logout...")
try:
    response = client.get('/accounts/logout/')
    print(f"Статус ответа: {response.status_code}")
    if response.status_code == 302:
        print(f"Redirect to: {response.url}")
        print("Logout работает правильно (перенаправляет)")
    else:
        print("Logout не работает как ожидалось")
except Exception as e:
    print(f"Ошибка при проверке logout: {e}")

# Проверяем, что пользователь действительно выходит
print("\nПроверяем выход пользователя...")
try:
    # Создаем тестового пользователя
    user = User.objects.filter(is_active=True).first()
    if user:
        print(f"Тестовый пользователь: {user.username}")
        
        # Логинимся
        client.force_login(user)
        response = client.get('/movies/')
        if response.context and response.context.get('user'):
            logged_in = response.context['user'].is_authenticated
            print(f"Пользователь до logout: {logged_in}")
        
        # Выполняем logout
        response = client.get('/accounts/logout/')
        
        # Проверяем после logout
        response = client.get('/movies/')
        if response.context and response.context.get('user'):
            logged_out = not response.context['user'].is_authenticated
            print(f"Пользователь после logout: {not response.context['user'].is_authenticated}")
            print("Logout работает правильно!" if logged_out else "Logout не сработал")
        else:
            print("Не удалось проверить статус пользователя после logout")
    else:
        print("Нет активных пользователей для теста")
except Exception as e:
    print(f"Ошибка при тестировании logout: {e}")
