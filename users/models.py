from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from datetime import timedelta


def _default_token() -> str:
    # Used only as a historical default in old migrations (users.0009-0011).
    import random
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


def _default_expires_at():
    # Used only as a historical default in old migrations (users.0009-0011).
    return timezone.now() + timedelta(minutes=15)


def _default_verification_code():
    # Used only as a historical default in old migrations (users.0011).
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
