#!/usr/bin/env python
"""
Прямой тест Telegram бота без webhook
"""
import os
import sys
import django

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from users.telegram_bot import telegram_bot
from users.models import TelegramVerificationToken
from django.contrib.auth import get_user_model

User = get_user_model()

def send_test_message():
    """Отправить тестовое сообщение напрямую"""
    print("🤖 Тестирование прямого взаимодействия с ботом...")
    
    if not telegram_bot.is_configured():
        print("❌ Бот не настроен")
        return
    
    # Получаем информацию о боте
    try:
        # Для python-telegram-bot 21.x нужно использовать async/await
        import asyncio
        
        async def get_bot_info():
            bot_info = await telegram_bot.bot.get_me()
            print(f"📋 Имя бота: {bot_info.first_name}")
            print(f"🔗 Username: @{bot_info.username}")
            print(f"🆔 ID бота: {bot_info.id}")
            return bot_info
        
        asyncio.run(get_bot_info())
        
    except Exception as e:
        print(f"❌ Ошибка получения информации о боте: {e}")
    
    print("\n📤 Для тестирования отправки сообщения:")
    print("1. Найдите бота в Telegram")
    print("2. Отправьте ему любое сообщение")
    print("3. Бот должен ответить согласно инструкции /start")
    
    # Создаем тестовый токен для проверки
    try:
        test_user = User.objects.first()
        if test_user:
            # Удаляем старые токены
            TelegramVerificationToken.objects.filter(user=test_user).delete()
            
            # Создаем новый токен
            token = TelegramVerificationToken.objects.create(user=test_user)
            print(f"\n📝 Тестовый код для {test_user.username}: {token.token}")
            print("⏰ Код действителен 15 минут")
            print("📋 Отправьте этот код боту для тестирования")
            
    except Exception as e:
        print(f"❌ Ошибка создания токена: {e}")

def test_verification_logic():
    """Тестирование логики верификации"""
    print("\n🔧 Тестирование логики верификации...")
    
    try:
        test_user = User.objects.first()
        if not test_user:
            print("❌ Нет пользователей в базе")
            return
        
        # Создаем токен
        token = TelegramVerificationToken.objects.create(user=test_user)
        print(f"📝 Создан токен: {token.token}")
        
        # Тестируем проверку с правильным кодом
        fake_chat_id = "123456789"
        result = telegram_bot.verify_code(fake_chat_id, token.token)
        print(f"✅ Результат проверки: {result}")
        
        # Проверяем, что chat_id сохранился
        token.refresh_from_db()
        print(f"💾 Chat ID сохранен: {token.chat_id}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 RV КИНО - Прямой тест Telegram бота")
    print("=" * 50)
    
    send_test_message()
    test_verification_logic()
    
    print("\n" + "=" * 50)
    print("📋 ИНСТРУКЦИЯ ПО ТЕСТИРОВАНИЮ:")
    print("=" * 50)
    print("1. ✅ Бот настроен и работает")
    print("2. 📱 Найдите бота в Telegram по username")
    print("3. 💬 Отправьте /start для получения инструкции")
    print("4. 🔢 Отправьте 6-значный код с сайта")
    print("5. 🌐 На сайте введите тот же код в форму")
    print("\n⚠️  ВАЖНО: Webhook работает только с ngrok!")
    print("💡 Для полного тестирования используйте setup_ngrok.py")
