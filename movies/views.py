from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie
from .models import Series

def index(request):
    movies = Movie.objects.filter(is_active=True).order_by('-created_at')[:12]
    series = Series.objects.filter(is_active=True).order_by('-created_at')[:12]

    # hero: последние 5 (фильмы+сериалы)
    mixed = []

    for m in movies:
        mixed.append({
            "kind": "movie",
            "id": m.id,
            "title": m.title,
            "poster": m.poster.url if m.poster else "",
            "rating": m.rating,
            "year": m.year,
        })

    for s in series:
        mixed.append({
            "kind": "series",
            "id": s.id,
            "title": s.title,
            "poster": s.poster.url if s.poster else "",
            "rating": s.rating,
            "year": s.year,
        })

    hero_items = sorted(mixed, key=lambda x: x["year"], reverse=True)[:5]  # или по created_at, если добавишь его в dict

    context = {
        "movies": movies,
        "series": series,
        "hero_items": hero_items,
        "page_title": "RV КИНО - Главная",
    }
    return render(request, "movies/index.html", context)


# Фильмы
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

def movie_watch(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if movie.video_url:
        return redirect(movie.video_url)
    return render(request, 'movies/not_available.html', {'obj': movie, 'type': 'фильм'})

def movie_watch_trailer(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if movie.trailer_url:
        return redirect(movie.trailer_url)
    return render(request, 'movies/not_available.html', {'obj': movie, 'type': 'фильм'})

# Сериалы
def series_list(request):
    series = Series.objects.filter(is_active=True)
    return render(request, 'movies/series.html', {'series': series, 'page_title': 'Каталог сериалов'})


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

def series_watch(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    if series.video_url:
        return redirect(series.video_url)
    return render(request, 'movies/not_available.html', {'obj': series, 'type': 'сериал'})

def series_watch_trailer(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    if series.trailer_url:
        return redirect(series.trailer_url)
    return render(request, 'movies/not_available.html', {'obj': series, 'type': 'сериал'})

#О нас
def about(request):
    """Страница О нас"""
    context = {
        'page_title': 'О компании RV КИНО'
    }
    return render(request, 'movies/about.html', context)