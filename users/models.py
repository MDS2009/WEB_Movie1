from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

import secrets
from datetime import timedelta


def _default_token() -> str:
    import random
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


def _default_expires_at():
    return timezone.now() + timedelta(minutes=15)


def _default_verification_code():
    """Генерирует алфавитно-цифровой код для верификации"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True, unique=True)
    can_create_community = models.BooleanField('Может создавать сообщества', default=False)
    accepted_privacy = models.BooleanField(default=False)
    accepted_terms = models.BooleanField(default=False)
    accepted_data_processing = models.BooleanField('Согласие на обработку персональных данных', default=False)
    accepted_at = models.DateTimeField(blank=True, null=True)
    phone_verified_at = models.DateTimeField('Подтверждён телефон (дата)', blank=True, null=True)
    telegram_chat_id = models.CharField('Telegram Chat ID', max_length=50, blank=True, null=True, unique=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль: {self.user}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Community(models.Model):
    """Сообщество пользователей"""
    name = models.CharField('Название сообщества', max_length=255, unique=True)
    slug = models.SlugField('Слаг', max_length=255, unique=True, blank=True)
    description = models.TextField('Описание сообщества', blank=True)
    members = models.TextField('Участники сообщества', blank=True)
    contact_info = models.CharField('Контактная информация', max_length=500, blank=True)
    avatar = models.ImageField('Аватар сообщества', upload_to='communities/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_communities')
    members_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='communities')
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name) or 'community'
            suffix = 1
            slug = base_slug
            while Community.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)


class PhoneVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='phone_verification_tokens')
    token = models.CharField(max_length=6, default=_default_token, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=_default_expires_at)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Токен подтверждения телефона'
        verbose_name_plural = 'Токены подтверждения телефона'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"PhoneVerificationToken(user={self.user_id}, used={bool(self.used_at)})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_active(self) -> bool:
        return (self.used_at is None) and (not self.is_expired)


class TelegramVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_verification_tokens')
    token = models.CharField(max_length=6, default=_default_token, db_index=True)
    chat_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=_default_expires_at)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Токен подтверждения Telegram'
        verbose_name_plural = 'Токены подтверждения Telegram'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"TelegramVerificationToken(user={self.user_id}, chat_id={self.chat_id}, used={bool(self.used_at)})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_active(self) -> bool:
        return (self.used_at is None) and (not self.is_expired)


class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=6, default=_default_token, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=_default_expires_at)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Токен сброса пароля'
        verbose_name_plural = 'Токены сброса пароля'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"PasswordResetToken(user={self.user_id}, used={bool(self.used_at)})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_active(self) -> bool:
        return (self.used_at is None) and (not self.is_expired)


class PasswordResetVerification(models.Model):
    """Модель для двухфакторной верификации сброса пароля через Telegram"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_reset_verifications')
    verification_code = models.CharField(max_length=8, default=_default_verification_code, db_index=True)
    reset_token = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=_default_expires_at)
    verified_at = models.DateTimeField(blank=True, null=True)
    failed_attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)

    class Meta:
        verbose_name = 'Верификация сброса пароля'
        verbose_name_plural = 'Верификации сброса пароля'
        indexes = [
            models.Index(fields=['verification_code']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"PasswordResetVerification(user={self.user_id}, code={self.verification_code}, verified={bool(self.verified_at)})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_active(self) -> bool:
        return (self.verified_at is None) and (not self.is_expired) and (self.failed_attempts < self.max_attempts)

    @property
    def can_attempt(self) -> bool:
        return self.failed_attempts < self.max_attempts

    def increment_failed_attempts(self):
        """Увеличивает счетчик неудачных попыток"""
        self.failed_attempts += 1
        self.save(update_fields=['failed_attempts'])

    def mark_verified(self, reset_token: str):
        """Отмечает верификацию как успешную"""
        self.verified_at = timezone.now()
        self.reset_token = reset_token
        self.save(update_fields=['verified_at', 'reset_token'])
