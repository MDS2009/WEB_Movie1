import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvkino.settings')
django.setup()

from django.conf import settings
from users.telegram_bot import telegram_bot

print(f'Bot token configured: {telegram_bot.is_configured()}')
token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
if token:
    print(f'Bot token: {token[:10]}...')
else:
    print('Bot token: NOT_SET')
print(f'Bot username: {getattr(settings, "TELEGRAM_BOT_USERNAME", "NOT_SET")}')
