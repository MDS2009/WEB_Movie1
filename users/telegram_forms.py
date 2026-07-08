from django import forms
from .models import UserProfile

class TelegramConnectForm(forms.Form):
    """Форма для подключения Telegram аккаунта"""
    telegram_code = forms.CharField(
        label='Код из Telegram бота',
        max_length=10,
        required=True,
        help_text='Введите код, который прислал вам Telegram бот'
    )

class UserProfileForm(forms.ModelForm):
    """Расширенная форма профиля с поддержкой Telegram"""
    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone', 'telegram_chat_id']
        widgets = {
            'telegram_chat_id': forms.HiddenInput(),  # Скрытое поле, заполняется автоматически
        }
