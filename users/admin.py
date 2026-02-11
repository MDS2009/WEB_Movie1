from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'accepted_privacy', 'accepted_terms', 'accepted_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['accepted_privacy', 'accepted_terms']
