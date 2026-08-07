from django.contrib import admin
from .models import UserProfile, Community, CommunityMembership


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'can_create_community', 'phone', 'yandex_id', 'accepted_privacy', 'accepted_terms', 'accepted_at']
    search_fields = ['user__username', 'user__email', 'phone', 'yandex_id']
    list_filter = ['can_create_community', 'accepted_privacy', 'accepted_terms']

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'avatar', 'phone', 'can_create_community')
        }),
        ('Вход через соцсети', {
            'fields': ('yandex_id',),
            'classes': ('collapse',)
        }),
        ('Согласия', {
            'fields': ('accepted_privacy', 'accepted_terms', 'accepted_data_processing', 'accepted_at'),
            'classes': ('collapse',)
        }),
    )


class CommunityMembershipInline(admin.TabularInline):
    model = CommunityMembership
    extra = 0
    autocomplete_fields = []


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'created_by', 'members_users_count', 'is_active', 'created_at']
    list_editable = ['sort_order']
    search_fields = ['name', 'description', 'created_by__username']
    list_filter = ['is_active', 'created_at']
    ordering = ['sort_order', 'name']
    inlines = [CommunityMembershipInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'avatar', 'is_active', 'sort_order')
        }),
        ('Участники и контакты', {
            'fields': ('members', 'contact_info', 'created_by')
        }),
    )

    def members_users_count(self, obj):
        return obj.members_users.count()
    members_users_count.short_description = 'Кол-во участников'


@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'community', 'role', 'joined_at']
    list_filter = ['role']
    search_fields = ['user__username', 'community__name']
