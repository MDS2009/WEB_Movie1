from django.contrib import admin
from .models import PhoneVerificationToken, PasswordResetToken, TelegramVerificationToken, UserProfile, Community


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'can_create_community', 'phone', 'phone_verified_at', 'telegram_chat_id', 'accepted_privacy', 'accepted_terms', 'accepted_at']
    search_fields = ['user__username', 'user__email', 'phone']
    list_filter = ['can_create_community', 'accepted_privacy', 'accepted_terms']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'avatar', 'phone', 'can_create_community')
        }),
        ('Согласия', {
            'fields': ('accepted_privacy', 'accepted_terms', 'accepted_at', 'phone_verified_at', 'telegram_chat_id'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'members_users_count', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    list_filter = ['is_active', 'created_at']
    filter_horizontal = ['members_users']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'avatar', 'is_active')
        }),
        ('Участники и контакты', {
            'fields': ('members', 'contact_info', 'created_by', 'members_users')
        }),
    )
    
    def members_users_count(self, obj):
        return obj.members_users.count()
    members_users_count.short_description = 'Кол-во участников'


@admin.register(PhoneVerificationToken)
class PhoneVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'expires_at', 'used_at']
    search_fields = ['user__username', 'user__profile__phone', 'token']
    list_filter = ['used_at']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'used_at']
    search_fields = ['user__username', 'user__email', 'token']
    list_filter = ['used_at']


@admin.register(TelegramVerificationToken)
class TelegramVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'chat_id', 'created_at', 'expires_at', 'used_at']
    search_fields = ['user__username', 'user__email', 'token', 'chat_id']
    list_filter = ['used_at']
