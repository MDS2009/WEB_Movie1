from django.shortcuts import render, get_object_or_404
from .models import Movie
from .models import Series

def index(request):
    """Главная страница"""
    # Получаем последние 6 фильмов
    movies = Movie.objects.filter(is_active=True).order_by('-created_at')[:6]

    context = {
        'movies': movies,
        'page_title': 'RV КИНО - Главная'
    }
    return render(request, 'movies/index.html', context)


def movies_list(request):
    """Каталог всех фильмов"""
    # Получаем все активные фильмы
    movies = Movie.objects.filter(is_active=True)

    context = {
        'movies': movies,
        'page_title': 'Каталог фильмов'
    }
    return render(request, 'movies/films.html', context)


def movie_detail(request, movie_id):
    """Детальная страница фильма"""
    # Получаем фильм по ID или показываем 404
    movie = get_object_or_404(Movie, id=movie_id, is_active=True)

    # Увеличиваем счётчик просмотров
    movie.views += 1
    movie.save()

    context = {
        'movie': movie,
        'page_title': movie.title
    }
    return render(request, 'movies/detail.html', context)

def series_list(request):
    # Получаем только сериалы
    series = Movie.objects.filter(type='series', is_active=True)
    context = {
        'series': series,
        'page_title': 'Сериалы'
    }
    return render(request, 'movies/series.html', context)

def series_detail(request, series_id):
    """Детальная страница сериала"""
    # Получаем сериал по ID или показываем 404
    series = get_object_or_404(Series, id=series_id, is_active=True)

    # Увеличиваем счётчик просмотров
    series.views += 1
    series.save()

    context = {
        'series': series,
        'page_title': series.title
    }
    return render(request, 'movies/detail_series.html', context)



def about(request):
    """Страница О нас"""
    context = {
        'page_title': 'О компании RV КИНО'
    }
    return render(request, 'movies/about.html', context)