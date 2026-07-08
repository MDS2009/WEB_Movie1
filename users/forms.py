from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import UserProfile, Community


def _normalize_ru_phone(raw: str) -> str:
    """
    Принимаем только российские номера и приводим к формату +7XXXXXXXXXX.
    """
    if not raw:
        raise ValidationError('Введите номер телефона.')

    digits = ''.join(ch for ch in raw if ch.isdigit())

    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits

    if len(digits) != 11 or not digits.startswith('7'):
        raise ValidationError('Введите российский номер в формате +7XXXXXXXXXX.')

    return f'+{digits}'


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=False)
    phone = forms.CharField(
        label='Телефон (обязательное поле)', 
        max_length=20, 
        required=True, 
        help_text='Нужен для входа и подтверждения аккаунта',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите номер телефона',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError('Телефон является обязательным полем.')

        phone = phone.strip()
        normalized = _normalize_ru_phone(phone)

        if UserProfile.objects.filter(phone=normalized).exists():
            raise ValidationError('Пользователь с таким телефоном уже зарегистрирован.')

        return normalized

    def save(self, commit=True):
        user = super().save(commit=commit)
        phone = self.cleaned_data.get('phone')
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if phone:
            profile.phone = phone
            profile.save(update_fields=['phone'])
        return user


class OrganizationRegisterForm(UserRegisterForm):
    organization_name = forms.CharField(
        label='Название организации',
        max_length=255,
        required=True,
    )

    class Meta(UserRegisterForm.Meta):
        fields = ['username', 'organization_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_organization = True
        profile.organization_name = self.cleaned_data.get('organization_name', '')
        profile.save(update_fields=['phone', 'is_organization', 'organization_name'])
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    phone = forms.CharField(
        label='Телефон',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите номер телефона',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return None
        
        phone = phone.strip()
        
        # Простая валидация - просто убираем все кроме цифр и добавляем +
        digits = ''.join(ch for ch in phone if ch.isdigit())
        if len(digits) == 11 and digits.startswith('7'):
            normalized = f'+{digits}'
        elif len(digits) == 10:
            normalized = f'+7{digits}'
        elif len(digits) == 11 and digits.startswith('8'):
            normalized = f'+7{digits[1:]}'
        else:
            raise ValidationError('Введите номер в формате +7XXXXXXXXXX или 8XXXXXXXXXX')

        # Проверяем уникальность
        qs = UserProfile.objects.filter(phone=normalized)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Этот номер уже используется другим пользователем.')

        return normalized


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'members', 'contact_info', 'avatar']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'members': forms.Textarea(attrs={'rows': 3}),
            'contact_info': forms.TextInput(attrs={'placeholder': 'Телефон: +7 (999) 123-45-67, Email: info@example.com'})
        }


class CommunityEditForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'members', 'contact_info', 'avatar', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'members': forms.Textarea(attrs={'rows': 3}),
            'contact_info': forms.TextInput(attrs={'placeholder': 'Телефон: +7 (999) 123-45-67, Email: info@example.com'})
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return None

        normalized = _normalize_ru_phone(phone)

        qs = UserProfile.objects.filter(phone=normalized)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Этот номер телефона уже используется другим пользователем.')

        return normalized


class PasswordResetRequestForm(forms.Form):
    phone = forms.CharField(
        label='Телефон', 
        required=True, 
        help_text='Введите номер телефона привязанный к аккаунту',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите номер телефона',
            'class': 'form-control'
        })
    )


class PasswordResetSetForm(SetPasswordForm):
    pass


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Телефон или имя пользователя',
        max_length=150,
    )
