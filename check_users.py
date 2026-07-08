#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
users = User.objects.all()
print('Всего пользователей:', users.count())

for user in users[:10]:  # Показываем первых 10 пользователей
    if hasattr(user, 'profile'):
        print(f'Пользователь: {user.username}')
        print(f'  Телефон: {user.profile.phone or "Не указан"}')
        print(f'  Telegram chat_id: {user.profile.telegram_chat_id or "Не привязан"}')
        print(f'  Email: {user.email or "Не указан"}')
        print('---')
    else:
        print(f'Пользователь: {user.username} - нет профиля')
        print('---')
