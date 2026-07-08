from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .forms import _normalize_ru_phone
from .models import UserProfile


class PhoneOrUsernameBackend(ModelBackend):
    """
    Аутентификация по телефону (из профиля) или имени пользователя.
    В форме логина вводится телефон ИЛИ username в одно поле.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        user = None

        # Сначала пробуем найти по username
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            user = None

        # Если по username не нашли — пробуем интерпретировать ввод как телефон
        if user is None:
            normalized_phone = None
            try:
                normalized_phone = _normalize_ru_phone(username)
            except Exception:
                # Ввели не телефон — оставляем normalized_phone = None
                pass

            if normalized_phone:
                profile = (
                    UserProfile.objects.filter(phone=normalized_phone)
                    .select_related('user')
                    .first()
                )
                if profile:
                    user = profile.user

        if user is None:
            return None

        if not self.user_can_authenticate(user):
            return None

        if user.check_password(password):
            return user

        return None

