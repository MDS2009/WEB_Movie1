from django.contrib import admin
from .models import (
    Movie,
    Series,
    Show,
    Genre,
    HeroSlide,
    FavoriteMovie,
    FavoriteSeries,
    FavoriteShow,
    MovieReview,
    SeriesReview,
    ShowReview,
)

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
        'slug',
        'description',
        'age_rating',
        'actors',
        'director',
        'producer',
        'poster',
        'year',
        'duration',
        'rating',
        'is_active',
        'views',
        'created_at',
        'video_url',
        'trailer_url',
        'genres',
    ]

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
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
        'slug',
        'description',
        'age_rating',
        'actors',
        'director',
        'producer',
        'poster',
        'year',
        'duration',
        'rating',
        'is_active',
        'views',
        'created_at',
        'video_url',
        'trailer_url',
        'genres',
    ]


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ['title', 'year', 'rating', 'views', 'is_active', 'created_at']
    list_filter = ['is_active', 'year', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['views', 'created_at']
    fields = [
        'title',
        'slug',
        'description',
        'age_rating',
        'actors',
        'director',
        'producer',
        'poster',
        'year',
        'duration',
        'rating',
        'is_active',
        'views',
        'created_at',
        'video_url',
        'trailer_url',
        'genres',
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'movie', 'series', 'is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['title', 'movie__title', 'series__title']


@admin.register(FavoriteMovie)
class FavoriteMovieAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'created_at']
    search_fields = ['user__username', 'movie__title']
    list_filter = ['created_at']


@admin.register(FavoriteSeries)
class FavoriteSeriesAdmin(admin.ModelAdmin):
    list_display = ['user', 'series', 'created_at']
    search_fields = ['user__username', 'series__title']
    list_filter = ['created_at']


@admin.register(FavoriteShow)
class FavoriteShowAdmin(admin.ModelAdmin):
    list_display = ['user', 'show', 'created_at']
    search_fields = ['user__username', 'show__title']
    list_filter = ['created_at']


@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ['movie', 'user', 'rating', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['movie__title', 'user__username', 'text']


@admin.register(SeriesReview)
class SeriesReviewAdmin(admin.ModelAdmin):
    list_display = ['series', 'user', 'rating', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['series__title', 'user__username', 'text']


@admin.register(ShowReview)
class ShowReviewAdmin(admin.ModelAdmin):
    list_display = ['show', 'user', 'rating', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['show__title', 'user__username', 'text']