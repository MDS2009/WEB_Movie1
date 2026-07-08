from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, TelegramVerificationToken, PasswordResetVerification, PasswordResetToken
from .telegram_forms import TelegramConnectForm
from .telegram_bot import telegram_bot
import secrets
import json
import logging

@login_required
def telegram_connect(request):
    """Страница подключения Telegram"""
    profile = request.user.profile
    verification_code = None
    
    if request.method == 'POST':
        form = TelegramConnectForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['telegram_code']
            
            # Ищем активный токен для этого пользователя
            try:
                token = TelegramVerificationToken.objects.filter(
                    user=request.user,
                    token=code,
                    used_at__isnull=True
                ).first()
                
                if not token:
                    messages.error(request, 'Неверный код. Попробуйте еще раз.')
                elif token.is_expired:
                    messages.error(request, 'Срок действия кода истек. Запросите новый код.')
                elif not token.chat_id:
                    messages.error(request, 'Сначала отправьте код боту в Telegram.')
                else:
                    # Подключаем Telegram
                    profile.telegram_chat_id = token.chat_id
                    profile.save(update_fields=['telegram_chat_id'])
                    
                    # Помечаем токен как использованный
                    token.used_at = timezone.now()
                    token.save(update_fields=['used_at'])
                    
                    messages.success(request, 'Telegram успешно подключен!')
                    return redirect('users:profile')
                    
            except Exception as e:
                messages.error(request, 'Произошла ошибка. Попробуйте еще раз.')
    else:
        # Создаем новый токен при GET запросе
        TelegramVerificationToken.objects.filter(
            user=request.user,
            used_at__isnull=True
        ).delete()  # Удаляем старые токены
        
        token = TelegramVerificationToken.objects.create(user=request.user)
        verification_code = token.token
        form = TelegramConnectForm()
    
    return render(request, 'users/telegram_connect.html', {
        'form': form,
        'telegram_connected': bool(profile.telegram_chat_id),
        'bot_username': getattr(settings, 'TELEGRAM_BOT_USERNAME', '@rvkino_bot'),
        'verification_code': verification_code
    })

@login_required
@require_POST
def telegram_disconnect(request):
    """Отключение Telegram"""
    profile = request.user.profile
    profile.telegram_chat_id = None
    profile.save(update_fields=['telegram_chat_id'])
    return JsonResponse({'success': True})

logger = logging.getLogger(__name__)

@csrf_exempt
def telegram_webhook(request):
    """
    Вебхук для Telegram бота
    Этот endpoint получает все обновления от Telegram API
    """
    if not telegram_bot.is_configured():
        return JsonResponse({'status': 'error', 'message': 'Bot not configured'}, status=503)
    
    try:
        data = json.loads(request.body)
        logger.info(f"Получено обновление от Telegram: {data.get('update_id')}")
        
        # Проверяем, что это сообщение
        if 'message' in data:
            message = data['message']
            chat_id = str(message['chat']['id'])
            text = message.get('text', '').strip()
            
            logger.info(f"Сообщение от {chat_id}: {text}")
            
            # Обработка команды /start
            if text == '/start':
                return handle_start_command(chat_id)
            
            # Обработка команды /help
            elif text == '/help':
                return handle_help_command(chat_id)
            
            # Обработка команды /reset_password
            elif text == '/reset_password':
                return handle_reset_password_command(chat_id)
            
            # Если пользователь отправляет 8-значный код верификации
            elif len(text) == 8 and text.isalnum():
                return handle_password_reset_verification(chat_id, text)
            
            # Если пользователь отправляет 6-значный код
            elif text.isdigit() and len(text) == 6:
                return handle_verification_code(chat_id, text)
            
            # Обработка других сообщений
            else:
                return handle_other_message(chat_id)
        
        # Обработка callback queries (кнопки inline)
        if 'callback_query' in data:
            return handle_callback_query(data['callback_query'])
        
        return JsonResponse({'status': 'ok'})
        
    except json.JSONDecodeError as e:
        logger.error(f"Невалидный JSON в webhook: {e}")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Internal error'}, status=500)

def handle_start_command(chat_id: str) -> JsonResponse:
    """Обработка команды /start"""
    welcome_text = (
        "🎬 *Добро пожаловать в RV КИНО бот!*\n\n"
        "Я помогу вам подключить Telegram к вашему аккаунту на сайте RV КИНО для получения уведомлений.\n\n"
        "*📋 Как подключить Telegram:*\n"
        "1️⃣ Зайдите на сайт RV КИНО и авторизуйтесь\n"
        "2️⃣ Перейдите в свой профиль\n"
        "3️⃣ Нажмите кнопку *\"Подключить Telegram\"*\n"
        "4️⃣ Скопируйте 6-значный код с сайта\n"
        "5️⃣ Отправьте этот код мне в этот чат\n"
        "6️⃣ Введите тот же код в форму на сайте для завершения\n\n"
        "*⚡ Что вы получите после подключения:*\n"
        "• Уведомления о новых фильмах\n"
        "• Напоминания о просмотренных фильмах\n"
        "• Информацию об обновлениях в ваших сообществах\n"
        "• Быстрый доступ к вашему профилю\n\n"
        "*❓ Нужна помощь?*\n"
        "Если у вас возникли вопросы, обратитесь в поддержку на сайте RV КИНО.\n\n"
        "Готовы начать? Просто отправьте мне 6-значный код с сайта! 🚀"
    )
    
    telegram_bot.bot.send_message(
        chat_id=chat_id,
        text=welcome_text,
        parse_mode='Markdown'
    )
    
    return JsonResponse({'status': 'ok', 'action': 'start'})

def handle_help_command(chat_id: str) -> JsonResponse:
    """Обработка команды /help"""
    help_text = (
        "🤖 *RV КИНО Бот - Справка*\n\n"
        "*📋 Доступные команды:*\n"
        "/start - Начать работу и получить инструкцию\n"
        "/help - Показать это справочное сообщение\n"
        "/reset_password - Сбросить пароль аккаунта\n\n"
        "*🔧 Как я работаю:*\n"
        "1. Получите 6-значный код на сайте RV КИНО для подключения Telegram\n"
        "2. Отправьте этот код мне\n"
        "3. Я подтвержу получение кода\n"
        "4. Завершите подключение на сайте\n\n"
        "*🔐 Сброс пароля:*\n"
        "1. Используйте команду /reset_password\n"
        "2. Следуйте инструкциям на сайте\n"
        "3. Отправьте 8-значный код верификации\n"
        "4. Получите ссылку для сброса пароля\n\n"
        "*⚠️ Важно:*\n"
        "• Коды действительны 15 минут\n"
        "• Каждый код уникален для вашего аккаунта\n"
        "• Один код можно использовать только один раз\n"
        "• У вас есть 3 попытки ввода кода сброса пароля\n\n"
        "*🎬 О RV КИНО:*\n"
        "Платформа для просмотра фильмов и создания сообществ по интересам.\n\n"
        "*❓ Нужна дополнительная помощь?*\n"
        "Обратитесь в поддержку на сайте RV КИНО."
    )
    
    telegram_bot.bot.send_message(
        chat_id=chat_id,
        text=help_text,
        parse_mode='Markdown'
    )
    
    return JsonResponse({'status': 'ok', 'action': 'help'})

def handle_verification_code(chat_id: str, code: str) -> JsonResponse:
    """Обработка 6-значного кода верификации"""
    result = telegram_bot.verify_code(chat_id, code)
    
    # Отправляем ответ пользователю
    telegram_bot.bot.send_message(
        chat_id=chat_id,
        text=result['message'],
        parse_mode='HTML'
    )
    
    # Логируем результат
    if result['success']:
        logger.info(f"Код {code} успешно подтвержден для chat_id: {chat_id}")
    else:
        logger.warning(f"Неверный код {code} от chat_id: {chat_id}")
    
    return JsonResponse({
        'status': 'ok',
        'action': 'verify_code',
        'success': result['success']
    })

def handle_other_message(chat_id: str) -> JsonResponse:
    """Обработка других сообщений"""
    help_text = (
        "🤖 *RV КИНО Бот*\n\n"
        "Я помогу вам подключить Telegram к вашему аккаунту на сайте RV КИНО.\n\n"
        "*🔧 Что делать:*\n"
        "1. Зайдите на сайт RV КИНО\n"
        "2. В профиле нажмите \"Подключить Telegram\"\n"
        "3. Отправьте мне 6-значный код с сайта\n\n"
        "*📋 Команды:*\n"
        "/start - Начать работу\n"
        "/help - Показать справку\n\n"
        "Готов к работе! Отправьте мне код с сайта 🚀"
    )
    
    telegram_bot.bot.send_message(
        chat_id=chat_id,
        text=help_text,
        parse_mode='Markdown'
    )
    
    return JsonResponse({'status': 'ok', 'action': 'other_message'})

def handle_callback_query(callback_query: dict) -> JsonResponse:
    """Обработка callback queries (inline кнопок)"""
    # Можно добавить обработку кнопок в будущем
    return JsonResponse({'status': 'ok', 'action': 'callback_query'})

def handle_reset_password_command(chat_id: str) -> JsonResponse:
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
    
    telegram_bot.bot.send_message(
        chat_id=chat_id,
        text=reset_text,
        parse_mode='Markdown'
    )
    
    return JsonResponse({'status': 'ok', 'action': 'reset_password'})

def handle_password_reset_verification(chat_id: str, code: str) -> JsonResponse:
    """Обработка 8-значного кода верификации сброса пароля"""
    try:
        # Ищем активную верификацию по коду
        verification = PasswordResetVerification.objects.filter(
            verification_code=code.upper(),
            verified_at__isnull=True
        ).select_related('user').first()
        
        if not verification:
            telegram_bot.bot.send_message(
                chat_id=chat_id,
                text="❌ *Неверный код верификации*\n\n"
                     "Проверьте правильность кода и попробуйте еще раз.\n"
                     "Код должен состоять из 8 символов.",
                parse_mode='Markdown'
            )
            return JsonResponse({'status': 'ok', 'action': 'invalid_code'})
        
        if verification.is_expired:
            telegram_bot.bot.send_message(
                chat_id=chat_id,
                text="⏰ *Срок действия кода истек*\n\n"
                     "Запросите новый код на сайте RV КИНО.\n"
                     "Код действителен 15 минут.",
                parse_mode='Markdown'
            )
            return JsonResponse({'status': 'ok', 'action': 'expired_code'})
        
        if not verification.can_attempt:
            telegram_bot.bot.send_message(
                chat_id=chat_id,
                text="🚫 *Превышено количество попыток*\n\n"
                     "Вы исчерпали лимит попыток ввода кода.\n\n"
                     "👨‍💻 *Нужна помощь?*\n"
                     "Свяжитесь со специалистом поддержки на сайте RV КИНО.",
                parse_mode='Markdown'
            )
            return JsonResponse({'status': 'ok', 'action': 'max_attempts'})
        
        # Проверяем соответствие chat_id
        user_profile = verification.user.profile
        if user_profile.telegram_chat_id != chat_id:
            verification.increment_failed_attempts()
            remaining_attempts = verification.max_attempts - verification.failed_attempts
            
            if remaining_attempts > 0:
                telegram_bot.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ *Неверный пользователь*\n\n"
                         f"Этот код привязан к другому аккаунту.\n\n"
                         f"🔄 Осталось попыток: {remaining_attempts}",
                    parse_mode='Markdown'
                )
            else:
                telegram_bot.bot.send_message(
                    chat_id=chat_id,
                    text="🚫 *Превышено количество попыток*\n\n"
                         "Вы исчерпали лимит попыток ввода кода.\n\n"
                         "👨‍💻 *Нужна помощь?*\n"
                         "Свяжитесь со специалистом поддержки на сайте RV КИНО.",
                    parse_mode='Markdown'
                )
            return JsonResponse({'status': 'ok', 'action': 'wrong_user'})
        
        # Все проверки пройдены - создаем токен сброса пароля
        reset_token = PasswordResetToken.objects.create(user=verification.user)
        
        # Отмечаем верификацию как успешную
        verification.mark_verified(reset_token.token)
        
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
        
        telegram_bot.bot.send_message(
            chat_id=chat_id,
            text=success_text,
            parse_mode='Markdown'
        )
        
        logger.info(f"Успешная верификация сброса пароля для chat_id: {chat_id}, user: {verification.user.username}")
        
        return JsonResponse({
            'status': 'ok',
            'action': 'reset_success',
            'user_id': verification.user.id
        })
        
    except Exception as e:
        logger.error(f"Ошибка при обработке кода сброса пароля: {e}", exc_info=True)
        
        telegram_bot.bot.send_message(
            chat_id=chat_id,
            text="⚠️ *Произошла ошибка*\n\n"
                 "Попробуйте еще раз или обратитесь в поддержку.",
            parse_mode='Markdown'
        )
        
        return JsonResponse({'status': 'error', 'message': str(e)})
