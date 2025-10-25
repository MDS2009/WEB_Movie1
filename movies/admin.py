
from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # Какие поля показывать в списке
    list_display = ['title', 'year', 'rating', 'views', 'is_active', 'created_at']

    # По каким полям можно фильтровать
    list_filter = ['is_active', 'year', 'created_at']

    # По каким полям можно искать
    search_fields = ['title', 'description']

    # Какие поля только для чтения
    readonly_fields = ['views', 'created_at']

    # Порядок полей в форме редактирования
    fields = [
        'title',
        'description', 
        'poster',
        'year',
        'duration',
        'rating',
        'is_active',
        'views',
        'created_at'
    ]