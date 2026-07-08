#!/usr/bin/env python
"""
Простой тест для проверки команды /reset_password
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from users.models import PasswordResetVerification, PasswordResetToken, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

def test_reset_password_flow():
    print("=== Тест системы сброса пароля ===")
    
    # Создаем тестового пользователя
    user, created = User.objects.get_or_create(
        username='test_reset_user',
        defaults={
            'email': 'test_reset@example.com',
            'password': 'testpass123'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Создан пользователь: {user.username}")
    
    # Настраиваем профиль
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.phone = '+79123456790'
    profile.telegram_chat_id = '999999999'  # Тестовый chat_id
    profile.save()
    print(f"✅ Профиль настроен: phone={profile.phone}, chat_id={profile.telegram_chat_id}")
    
    # Создаем верификацию
    verification = PasswordResetVerification.objects.create(user=user)
    print(f"✅ Создан код верификации: {verification.verification_code}")
    print(f"✅ Срок действия: до {verification.expires_at}")
    
    # Тестируем логику обработки кода
    print(f"\n--- Проверка логики обработки кода ---")
    
    # Имитируем получение кода от пользователя
    test_code = verification.verification_code
    test_chat_id = '999999999'
    
    print(f"Получен код: {test_code} от chat_id: {test_chat_id}")
    
    # Поиск верификации
    verification_obj = PasswordResetVerification.objects.filter(
        verification_code=test_code.upper(),
        verified_at__isnull=True
    ).select_related('user').first()
    
    if not verification_obj:
        print("❌ Код не найден")
        return
    
    if verification_obj.is_expired:
        print("❌ Код истек")
        return
    
    if not verification_obj.can_attempt:
        print("❌ Превышено количество попыток")
        return
    
    # Проверка chat_id
    user_profile = verification_obj.user.profile
    if user_profile.telegram_chat_id != test_chat_id:
        print("❌ Chat ID не совпадает")
        verification_obj.increment_failed_attempts()
        print(f"❌ Неудачная попытка: {verification_obj.failed_attempts}")
        return
    
    print("✅ Chat ID совпадает")
    print("✅ Все проверки пройдены")
    
    # Создание токена сброса пароля
    reset_token = PasswordResetToken.objects.create(user=verification_obj.user)
    verification_obj.mark_verified(reset_token.token)
    
    reset_url = f"http://127.0.0.1:8000/accounts/password-reset/confirm/{reset_token.token}/"
    
    print(f"✅ Создан токен сброса: {reset_token.token}")
    print(f"✅ Ссылка для сброса: {reset_url}")
    print(f"✅ Верификация отмечена как успешная")
    
    print(f"\n=== Тест успешно пройден! ===")
    print(f"Теперь бот должен ответить на код {test_code} сообщением со ссылкой для сброса пароля")

if __name__ == '__main__':
    test_reset_password_flow()
