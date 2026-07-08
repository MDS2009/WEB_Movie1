#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.views import _send_password_reset
from django.test import RequestFactory

User = get_user_model()

# Создаем фейковый request
factory = RequestFactory()
request = factory.post('/fake-path')

# Находим пользователя Test11
user = User.objects.get(username='Test11')
print(f"Тестируем сброс пароля для пользователя: {user.username}")
print(f"Телефон: {user.profile.phone}")
print(f"Telegram chat_id: {user.profile.telegram_chat_id}")

# Вызываем функцию сброса пароля
print("\n=== Вызов _send_password_reset ===")
_send_password_reset(request, user)
