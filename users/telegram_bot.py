import os
import logging
import asyncio
from asgiref.sync import sync_to_async
from telegram import Bot
from telegram.error import TelegramError
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import TelegramVerificationToken
import concurrent.futures

User = get_user_model()

logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.bot = None
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
    
    def is_configured(self):
        return self.bot is not None
    
    def send_verification_code(self, chat_id: str, code: str, purpose: str = 'подтверждения'):
        """Отправляет код верификации в Telegram"""
        if not self.is_configured():
            logger.error(f"Telegram бот не настроен. Не удалось отправить код {purpose}")
            return False
        
        try:
            message = f"🔐 Код {purpose} для RV КИНО: {code}\n\n⏰ Код действует 15 минут."
            
            # Используем синхронный метод для отправки
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Если мы уже в async контексте, создаем задачу
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run, 
                            self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
                        )
                        future.result(timeout=10)
                else:
                    asyncio.run(self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML'))
            except RuntimeError:
                # Fallback для синхронного контекста
                self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
            
            logger.info(f"Код {purpose} отправлен в Telegram chat_id: {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка отправки сообщения в Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Неизвестная ошибка при отправке в Telegram: {e}")
            return False
    
    def send_password_reset_code(self, chat_id: str, code: str, reset_url: str = None):
        """Отправляет код сброса пароля в Telegram"""
        if not self.is_configured():
            logger.error(f"Telegram бот не настроен. Не удалось отправить код сброса пароля")
            return False
        
        try:
            if reset_url:
                message = f"🔐 Код сброса пароля для RV КИНО: {code}\n\n🔗 Ссылка для сброса пароля: {reset_url}\n\n⏰ Код действует 15 минут."
            else:
                message = f"🔐 Код сброса пароля для RV КИНО: {code}\n\n⏰ Код действует 15 минут."
            
            # Используем синхронный метод для отправки
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Если мы уже в async контексте, создаем задачу
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run, 
                            self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
                        )
                        future.result(timeout=10)
                else:
                    asyncio.run(self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML'))
            except RuntimeError:
                # Fallback для синхронного контекста
                self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
            
            logger.info(f"Код сброса пароля отправлен в Telegram chat_id: {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка отправки сообщения в Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Неизвестная ошибка при отправке в Telegram: {e}")
            return False
    
    def send_phone_verification_code(self, chat_id: str, code: str):
        """Отправляет код подтверждения телефона в Telegram"""
        return self.send_verification_code(chat_id, code, 'подтверждения телефона')
    
    async def verify_code_async(self, chat_id: str, code: str):
        """Асинхронная проверка кода верификации через threading"""
        import concurrent.futures
        import threading
        
        def get_token_sync():
            """Синхронная функция для получения токена"""
            try:
                return TelegramVerificationToken.objects.filter(
                    token=code,
                    used_at__isnull=True
                ).first()
            except Exception as e:
                logger.error(f"Ошибка получения токена: {e}")
                return None
        
        def process_code_sync(chat_id_val, code_val):
            """Синхронная обработка кода в отдельном потоке"""
            try:
                token = TelegramVerificationToken.objects.filter(
                    token=code_val,
                    used_at__isnull=True
                ).first()
                
                if not token:
                    return {
                        'success': False,
                        'message': '❌ Неверный код. Проверьте правильность кода и попробуйте еще раз.'
                    }
                
                if token.is_expired:
                    return {
                        'success': False,
                        'message': '❌ Срок действия кода истек. Запросите новый код на сайте.'
                    }
                
                if token.chat_id and token.chat_id != chat_id_val:
                    return {
                        'success': False,
                        'message': '❌ Этот код уже используется другим пользователем.'
                    }
                
                # Привязываем chat_id к токену
                token.chat_id = chat_id_val
                token.save(update_fields=['chat_id'])
                
                # Получаем информацию о пользователе
                user = token.user
                username = user.get_full_name() or user.username
                
                return {
                    'success': True,
                    'message': f'✅ Код принят! Теперь {username} может завершить подключение на сайте.',
                    'user_info': {
                        'username': username,
                        'email': user.email
                    }
                }
                
            except Exception as e:
                logger.error(f"Ошибка в process_code_sync: {e}")
                return {
                    'success': False,
                    'message': '❌ Произошла ошибка. Попробуйте еще раз.'
                }
        
        # Запускаем в отдельном потоке
        try:
            loop = asyncio.get_event_loop()
            # Используем executor для запуска в отдельном потоке
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(process_code_sync, chat_id, code)
                result = await loop.run_in_executor(None, future.result)
                return result
        except Exception as e:
            logger.error(f"Ошибка проверки кода: {e}")
            return {
                'success': False,
                'message': '❌ Произошла ошибка. Попробуйте еще раз.'
            }
    
    def verify_code(self, chat_id: str, code: str):
        """Синхронная обертка для verify_code_async (для webhook)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если мы уже в async контексте, создаем новый loop
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result = new_loop.run_until_complete(self.verify_code_async(chat_id, code))
                new_loop.close()
                asyncio.set_event_loop(loop)
                return result
            else:
                return loop.run_until_complete(self.verify_code_async(chat_id, code))
        except RuntimeError:
            # Нет активного loop
            return asyncio.run(self.verify_code_async(chat_id, code))

# Глобальный экземпляр сервиса
telegram_bot = TelegramBotService()
