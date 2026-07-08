#!/usr/bin/env python
"""
Django management command to run Telegram bot
Usage: python manage.py run_telegram_bot [--mode polling|webhook]
"""
import os
import sys
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

# Настройка Django перед импортом бота
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')

# Импортируем после настройки Django
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from users.telegram_bot import telegram_bot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запускает Telegram бот для RV КИНО'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['polling', 'webhook'],
            default='polling',
            help='Режим работы бота: polling (для разработки) или webhook (для production)'
        )
        parser.add_argument(
            '--webhook-url',
            type=str,
            default=None,
            help='URL для webhook (требуется для режима webhook)'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        webhook_url = options['webhook_url']

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('🎬 RV КИНО - Django Telegram Bot'))
        self.stdout.write(self.style.SUCCESS('=' * 50))

        if not telegram_bot.is_configured():
            self.stdout.write(self.style.ERROR('❌ TELEGRAM_BOT_TOKEN не настроен'))
            self.stdout.write(self.style.WARNING('Проверьте .env файл'))
            sys.exit(1)

        # Создаем приложение бота
        application = Application.builder().token(telegram_bot.bot_token).build()

        # Настраиваем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("reset_password", self.reset_password_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        self.stdout.write(self.style.SUCCESS(f'🤖 Бот запускается в режиме: {mode}'))

        try:
            if mode == 'webhook':
                self.run_webhook_mode(application, webhook_url)
            else:
                self.run_polling_mode(application)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n🛑 Бот остановлен'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))
            logger.error(f"Ошибка запуска бота: {e}", exc_info=True)
            sys.exit(1)

    def run_polling_mode(self, application: Application):
        """Запуск в режиме polling"""
        self.stdout.write(self.style.WARNING('⚠️  Не закрывайте это окно'))
        self.stdout.write(self.style.NOTICE('🛑 Для остановки нажмите Ctrl+C'))
        application.run_polling()

    def run_webhook_mode(self, application: Application, webhook_url: str = None):
        """Запуск в режиме webhook"""
        if not webhook_url:
            site_url = getattr(settings, 'SITE_URL', None)
            if site_url:
                webhook_url = f"{site_url}/accounts/telegram/webhook/"
            else:
                self.stdout.write(self.style.ERROR('❌ WEBHOOK_URL или SITE_URL не настроен'))
                sys.exit(1)

        self.stdout.write(self.style.SUCCESS(f'🌐 Webhook URL: {webhook_url}'))

        # Для webhook режима нужно настроить сервер
        # В production используйте nginx + webhook
        port = int(os.environ.get('BOT_WEBHOOK_PORT', 8443))

        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="accounts/telegram/webhook/",
            webhook_url=webhook_url
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка /start"""
        welcome_text = (
            "🎬 *Добро пожаловать в RV КИНО бот!*\n\n"
            "Я помогу вам подключить Telegram к вашему аккаунту.\n\n"
            "*📋 Как подключить Telegram:*\n"
            "1️⃣ Зайдите на сайт RV КИНО и авторизуйтесь\n"
            "2️⃣ Перейдите в свой профиль\n"
            "3️⃣ Нажмите кнопку *\"Подключить Telegram\"*\n"
            "4️⃣ Скопируйте 6-значный код с сайта\n"
            "5️⃣ Отправьте этот код мне\n\n"
            "Готовы? Отправьте мне код с сайта! 🚀"
        )
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка /help"""
        help_text = (
            "🤖 *RV КИНО Бот - Справка*\n\n"
            "*📋 Команды:*\n"
            "/start - Начать работу\n"
            "/help - Показать справку\n"
            "/reset_password - Сбросить пароль аккаунта\n\n"
            "*🔧 Подключение Telegram:*\n"
            "1. Зайдите на сайт RV КИНО\n"
            "2. В профиле нажмите \"Подключить Telegram\"\n"
            "3. Отправьте мне 6-значный код\n\n"
            "*🔐 Сброс пароля:*\n"
            "1. Используйте команду /reset_password\n"
            "2. Следуйте инструкциям на сайте\n"
            "3. Отправьте 8-значный код верификации\n\n"
            "*⚠️ Важно:*\n"
            "• Коды действительны 15 минут\n"
            "• Каждый код уникален для вашего аккаунта\n"
            "• У вас есть 3 попытки ввода кода сброса пароля"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def reset_password_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /reset_password"""
        reset_text = (
            "🔐 *Сброс пароля - RV КИНО*\n\n"
            "Чтобы сбросить пароль, выполните следующие шаги:\n\n"
            "1️⃣ Зайдите на сайт RV КИНО\n"
            "2️⃣ На странице входа нажмите \"Забыли пароль?\"\n"
            "3️⃣ Введите ваш номер телефона\n"
            "4️⃣ Скопируйте 8-значный код верификации с сайта\n"
            "5️⃣ Отправьте этот код мне в этот чат\n\n"
            "📋 *Важно:*\n"
            "• Код действителен 15 минут\n"
            "• Код состоит из 8 символов (буквы и цифры)\n"
            "• У вас есть 3 попытки ввода\n\n"
            "Готовы? Отправьте мне 8-значный код! 🚀"
        )
        await update.message.reply_text(reset_text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщений"""
        text = update.message.text.strip()
        chat_id = str(update.message.chat.id)

        # Если пользователь отправляет 8-значный код верификации сброса пароля
        if len(text) == 8 and text.isalnum():
            await self.handle_password_reset_verification(update, chat_id, text)
        # Если 6-значный код
        elif text.isdigit() and len(text) == 6:
            result = await telegram_bot.verify_code_async(chat_id, text)
            await update.message.reply_text(result['message'], parse_mode='HTML')

            if result['success']:
                logger.info(f"Код {text} подтвержден для chat_id: {chat_id}")
            else:
                logger.warning(f"Неверный код {text} от chat_id: {chat_id}")
        else:
            help_text = (
                "🤖 *RV КИНО Бот*\n\n"
                "Я помогу вам подключить Telegram к вашему аккаунту и сбросить пароль.\n\n"
                "*🔧 Подключение Telegram:*\n"
                "Отправьте мне 6-значный код с сайта\n\n"
                "*🔐 Сброс пароля:*\n"
                "Используйте команду /reset_password\n\n"
                "*📋 Команды:*\n"
                "/start - Начать работу\n"
                "/help - Показать справку\n"
                "/reset_password - Сбросить пароль"
            )
            await update.message.reply_text(help_text, parse_mode='Markdown')

    async def handle_password_reset_verification(self, update: Update, chat_id: str, code: str):
        """Обработка 8-значного кода верификации сброса пароля"""
        try:
            from django.db import connections
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def get_verification(code_str):
                from users.models import PasswordResetVerification
                return PasswordResetVerification.objects.filter(
                    verification_code=code_str,
                    verified_at__isnull=True
                ).select_related('user').first()
            
            @sync_to_async
            def create_reset_token(user):
                from users.models import PasswordResetToken
                return PasswordResetToken.objects.create(user=user)
            
            @sync_to_async
            def mark_verification_verified(verification, reset_token_str):
                verification.mark_verified(reset_token_str)
            
            @sync_to_async
            def increment_failed_attempts(verification):
                verification.increment_failed_attempts()
            
            # Ищем активную верификацию по коду
            verification = await get_verification(code.upper())
            
            if not verification:
                await update.message.reply_text(
                    "❌ *Неверный код верификации*\n\n"
                    "Проверьте правильность кода и попробуйте еще раз.\n"
                    "Код должен состоять из 8 символов.",
                    parse_mode='Markdown'
                )
                return
            
            if verification.is_expired:
                await update.message.reply_text(
                    "⏰ *Срок действия кода истек*\n\n"
                    "Запросите новый код на сайте RV КИНО.\n"
                    "Код действителен 15 минут.",
                    parse_mode='Markdown'
                )
                return
            
            if not verification.can_attempt:
                await update.message.reply_text(
                    "🚫 *Превышено количество попыток*\n\n"
                    "Вы исчерпали лимит попыток ввода кода.\n\n"
                    "👨‍💻 *Нужна помощь?*\n"
                    "Свяжитесь со специалистом поддержки на сайте RV КИНО.",
                    parse_mode='Markdown'
                )
                return
            
            # Проверяем соответствие chat_id
            user_profile = verification.user.profile
            if user_profile.telegram_chat_id != chat_id:
                await increment_failed_attempts(verification)
                remaining_attempts = verification.max_attempts - verification.failed_attempts
                
                if remaining_attempts > 0:
                    await update.message.reply_text(
                        f"❌ *Неверный пользователь*\n\n"
                        f"Этот код привязан к другому аккаунту.\n\n"
                        f"🔄 Осталось попыток: {remaining_attempts}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        "🚫 *Превышено количество попыток*\n\n"
                        "Вы исчерпали лимит попыток ввода кода.\n\n"
                        "👨‍💻 *Нужна помощь?*\n"
                        "Свяжитесь со специалистом поддержки на сайте RV КИНО.",
                        parse_mode='Markdown'
                    )
                return
            
            # Все проверки пройдены - создаем токен сброса пароля
            reset_token = await create_reset_token(verification.user)
            
            # Отмечаем верификацию как успешную
            await mark_verification_verified(verification, reset_token.token)
            
            # Создаем ссылку для сброса пароля
            reset_url = f"http://127.0.0.1:8000/accounts/password-reset/confirm/{reset_token.token}/"
            
            success_text = (
                f"✅ *Верификация успешна!*\n\n"
                f"🔗 *Ваша ссылка для сброса пароля:*\n"
                f"{reset_url}\n\n"
                f"⏰ Ссылка действительна 15 минут.\n"
                f"🔒 Никому не передавайте эту ссылку!\n\n"
                f"Нажмите на ссылку, чтобы установить новый пароль."
            )
            
            await update.message.reply_text(success_text, parse_mode='Markdown')
            logger.info(f"Успешная верификация сброса пароля для chat_id: {chat_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке кода сброса пароля: {e}")
            await update.message.reply_text(
                "⚠️ *Произошла ошибка*\n\n"
                "Попробуйте еще раз или обратитесь в поддержку.",
                parse_mode='Markdown'
            )
