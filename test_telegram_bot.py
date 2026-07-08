#!/usr/bin/env python
"""
Скрипт для тестирования Telegram бота
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from users.telegram_bot import telegram_bot
from users.models import TelegramVerificationToken
from django.contrib.auth import get_user_model

User = get_user_model()

def test_bot_configuration():
    """Проверка конфигурации бота"""
    print("🤖 Тестирование Telegram бота...")
    print(f"📱 Токен настроен: {telegram_bot.is_configured()}")
    
    if telegram_bot.is_configured():
        print("✅ Бот настроен правильно")
        
        # Проверка информации о боте
        try:
            bot_info = telegram_bot.bot.get_me()
            print(f"📋 Имя бота: {bot_info.first_name}")
            print(f"🔗 Username: @{bot_info.username}")
            print(f"🆔 ID бота: {bot_info.id}")
        except Exception as e:
            print(f"❌ Ошибка получения информации о боте: {e}")
    else:
        print("❌ Бот не настроен - проверьте TELEGRAM_BOT_TOKEN в .env")
        return False
    
    return True

def test_token_verification():
    """Тестирование верификации токена"""
    print("\n🔧 Тестирование верификации кода...")
    
    try:
        # Создаем тестовый токен
        test_user = User.objects.first()
        if not test_user:
            print("❌ Нет пользователей в базе данных")
            return False
        
        # Удаляем старые токены
        TelegramVerificationToken.objects.filter(user=test_user).delete()
        
        # Создаем новый токен
        token = TelegramVerificationToken.objects.create(user=test_user)
        print(f"📝 Создан тестовый токен: {token.token}")
        print(f"👤 Пользователь: {test_user.username}")
        
        # Тестируем проверку кода
        result = telegram_bot.verify_code("123456789", token.token)
        print(f"🔍 Результат проверки: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования верификации: {e}")
        return False

def test_send_message():
    """Тестирование отправки сообщения (нужен реальный chat_id)"""
    print("\n📤 Тестирование отправки сообщения...")
    print("⚠️  Для этого теста нужен реальный chat_id")
    print("💡 Отправьте боту любое сообщение, чтобы получить chat_id")
    
    # Здесь можно добавить код для получения chat_id из логов или базы
    
if __name__ == "__main__":
    print("=" * 50)
    print("🎬 RV КИНО - Тестирование Telegram бота")
    print("=" * 50)
    
    # Тест 1: Конфигурация
    if not test_bot_configuration():
        print("\n❌ Исправьте конфигурацию бота и попробуйте снова")
        sys.exit(1)
    
    # Тест 2: Верификация
    test_token_verification()
    
    # Тест 3: Отправка сообщения
    test_send_message()
    
    print("\n✅ Тестирование завершено!")
    print("\n📋 Следующие шаги:")
    print("1. Убедитесь, что бот работает в Telegram")
    print("2. Для локального тестирования используйте ngrok или similar")
    print("3. Настройте webhook для production")
