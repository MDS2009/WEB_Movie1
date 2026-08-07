from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch, F
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from users.models import UserProfile
from users.models import Community, CommunityMembership

from .forms import ReviewForm
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
    CommunityProject,
    News,
)

CATALOG_SORTS = {
    'new': '-created_at',
    'rating': '-rating',
    'year': '-year',
    'popularity': '-views',
    'title': 'title',
}


def _apply_query_filter(queryset, query):
    if not query:
        return queryset
    query_variants = {query, query.lower(), query.upper(), query.casefold()}
    title_filter = Q()
    description_filter = Q()
    for value in query_variants:
        title_filter |= Q(title__contains=value)
        description_filter |= Q(description__contains=value)
    return queryset.filter(title_filter | description_filter)


def _apply_catalog_filters(queryset, query, sort_key):
    queryset = _apply_query_filter(queryset, query)
    order_by = CATALOG_SORTS.get(sort_key, CATALOG_SORTS['new'])
    return queryset.order_by(order_by)


def _build_item(obj, kind):
    return {
        'kind': kind,
        'id': obj.id,
        'slug': obj.slug,
        'title': obj.title,
        'poster': obj.poster.url if obj.poster else '',
        'rating': obj.rating,
        'year': obj.year,
        'views': obj.views,
        'created_at': obj.created_at,
    }

def index(request):
    movies = (
        Movie.objects.filter(is_active=True)
        .only('id', 'title', 'poster', 'rating', 'year', 'slug')
        .order_by('-created_at')[:12]
    )
    series = (
        Series.objects.filter(is_active=True)
        .only('id', 'title', 'poster', 'rating', 'year', 'slug')
        .order_by('-created_at')[:12]
    )
    shows = (
        Show.objects.filter(is_active=True)
        .only('id', 'title', 'poster', 'rating', 'year', 'slug')
        .order_by('-created_at')[:12]
    )

    slides = HeroSlide.objects.filter(is_active=True).select_related('movie', 'series')
    hero_items = []
    if slides.exists():
        for slide in slides:
            if slide.movie:
                hero_items.append(_build_item(slide.movie, 'movie'))
            elif slide.series:
                hero_items.append(_build_item(slide.series, 'series'))
            else:
                hero_items.append({
                    'kind': 'custom',
                    'id': slide.id,
                    'slug': '',
                    'title': slide.title or 'RV КИНО',
                    'poster': slide.poster.url if slide.poster else '',
                    'rating': '',
                    'year': '',
                    'url': slide.link_url or '',
                })
    else:
        mixed = []
        for m in movies:
            mixed.append({
                "kind": "movie",
                "id": m.id,
                "slug": m.slug,
                "title": m.title,
                "poster": m.poster.url if m.poster else "",
                "rating": m.rating,
                "year": m.year,
            })

        for s in series:
            mixed.append({
                "kind": "series",
                "id": s.id,
                "slug": s.slug,
                "title": s.title,
                "poster": s.poster.url if s.poster else "",
                "rating": s.rating,
                "year": s.year,
            })

        hero_items = sorted(mixed, key=lambda x: x["year"], reverse=True)[:5]

    communities = (
        Community.objects.filter(is_active=True)
        .select_related('created_by')
        .only('avatar', 'name', 'slug', 'sort_order', 'created_by__id', 'created_by__username')
        .order_by('sort_order', 'name')[:24]
    )

    context = {
        "movies": movies,
        "series": series,
        "shows": shows,
        "hero_items": hero_items,
        "communities": communities,
        "page_title": "RV КИНО - Главная",
    }
    return render(request, "movies/index.html", context)


def search(request):
    query = request.GET.get('q', '').strip()
    kind = request.GET.get('kind', 'all')
    genre_slug = request.GET.get('genre', '').strip()
    sort_key = request.GET.get('sort', 'new')

    genres = Genre.objects.all()
    search_results = []
    search_active = bool(query or genre_slug or kind != 'all' or sort_key != 'new')

    if search_active:
        if kind == 'communities':
            communities_qs = Community.objects.filter(is_active=True).select_related('created_by')
            if query:
                communities_qs = communities_qs.filter(
                    Q(name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(created_by__username__icontains=query)
                )
            search_results = [
                {
                    'kind': 'community',
                    'id': community.id,
                    'slug': community.slug,
                    'title': community.name,
                    'poster': community.avatar.url if community.avatar else '',
                    'rating': None,
                    'year': None,
                    'views': None,
                    'created_at': community.created_at,
                }
                for community in communities_qs.order_by('sort_order', 'name')[:24]
            ]
        else:
            movies_qs = Movie.objects.filter(is_active=True)
            series_qs = Series.objects.filter(is_active=True)
            shows_qs = Show.objects.filter(is_active=True)

            if query:
                movies_qs = _apply_query_filter(movies_qs, query)
                series_qs = _apply_query_filter(series_qs, query)
                shows_qs = _apply_query_filter(shows_qs, query)
            if genre_slug:
                movies_qs = movies_qs.filter(genres__slug=genre_slug)
                series_qs = series_qs.filter(genres__slug=genre_slug)
                shows_qs = shows_qs.filter(genres__slug=genre_slug)

            movies_qs = movies_qs.distinct()
            series_qs = series_qs.distinct()
            shows_qs = shows_qs.distinct()

            order_by = CATALOG_SORTS.get(sort_key, CATALOG_SORTS['new'])
            if kind == 'movies':
                search_results = [_build_item(obj, 'movie') for obj in movies_qs.order_by(order_by)[:24]]
            elif kind == 'series':
                search_results = [_build_item(obj, 'series') for obj in series_qs.order_by(order_by)[:24]]
            elif kind == 'shows':
                search_results = [_build_item(obj, 'show') for obj in shows_qs.order_by(order_by)[:24]]
            else:
                combined = [
                    _build_item(obj, 'movie') for obj in movies_qs.order_by(order_by)[:12]
                ] + [
                    _build_item(obj, 'series') for obj in series_qs.order_by(order_by)[:12]
                ] + [
                    _build_item(obj, 'show') for obj in shows_qs.order_by(order_by)[:12]
                ]

                if query:
                    news_qs = News.objects.filter(
                        is_published=True, published_at__lte=timezone.now()
                    ).filter(Q(title__icontains=query) | Q(content__icontains=query))
                    combined += [
                        {
                            'kind': 'news',
                            'id': item.id,
                            'slug': item.slug,
                            'title': item.title,
                            'poster': item.image.url if item.image else '',
                            'rating': None,
                            'year': None,
                            'views': None,
                            'created_at': item.published_at,
                        }
                        for item in news_qs.order_by('-published_at')[:6]
                    ]

                reverse = order_by.startswith('-')
                key_map = {
                    'title': lambda x: (x['title'] or '').lower(),
                    'rating': lambda x: x['rating'] or 0,
                    'year': lambda x: x['year'] or 0,
                    'popularity': lambda x: x['views'] or 0,
                    'new': lambda x: x['created_at'],
                }
                key_fn = key_map.get(sort_key, key_map['new'])
                search_results = sorted(combined, key=key_fn, reverse=reverse)[:24]

    context = {
        "genres": genres,
        "search_results": search_results,
        "search_active": search_active,
        "query": query,
        "kind": kind,
        "genre": genre_slug,
        "sort": sort_key,
        "page_title": "Поиск",
    }
    return render(request, "movies/search.html", context)


# Фильмы
def movies_list(request):
    """Каталог всех фильмов"""
    # Получаем все активные фильмы
    query = request.GET.get('q', '').strip()
    sort_key = request.GET.get('sort', 'new')
    movies = Movie.objects.filter(is_active=True).prefetch_related('genres')
    movies = _apply_catalog_filters(movies, query, sort_key)
    paginator = Paginator(movies, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'movies': page_obj,
        'page_obj': page_obj,
        'query': query,
        'sort': sort_key,
        'page_title': 'Каталог фильмов'
    }
    return render(request, 'movies/films.html', context)


def movie_detail(request, movie_id, slug=None):
    """Детальная страница фильма"""
    # Получаем фильм по ID или показываем 404
    movie = get_object_or_404(
        Movie.objects.prefetch_related(
            'genres',
            Prefetch('reviews', queryset=MovieReview.objects.filter(is_active=True)),
        ),
        id=movie_id,
        is_active=True,
    )
    if not movie.slug:
        movie.save()
    if slug is None or slug != movie.slug:
        return redirect('movies:detail', movie_id=movie.id, slug=movie.slug)

    increment_view = request.method == 'GET'
    view_cookie = f"viewed_movie_{movie.id}"
    if increment_view and not request.COOKIES.get(view_cookie):
        Movie.objects.filter(pk=movie.pk).update(views=F('views') + 1)
        movie.refresh_from_db(fields=['views'])

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteMovie.objects.filter(user=request.user, movie=movie).exists()

    reviews = movie.reviews.all()
    form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            MovieReview.objects.create(
                movie=movie,
                user=request.user,
                rating=form.cleaned_data['rating'],
                text=form.cleaned_data['text'],
            )
            messages.success(request, 'Отзыв добавлен.')
            return redirect('movies:detail', movie_id=movie.id, slug=movie.slug)

    similar_items = (
        Movie.objects.filter(is_active=True, genres__in=movie.genres.all())
        .exclude(id=movie.id)
        .distinct()
        .order_by('-rating')[:10]
    )

    context = {
        'movie': movie,
        'page_title': movie.title,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'review_form': form,
        'similar_items': similar_items,
    }
    response = render(request, 'movies/detail.html', context)
    if increment_view and not request.COOKIES.get(view_cookie):
        response.set_cookie(view_cookie, 'true', max_age=60 * 60 * 24 * 30, path='/')
    return response

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
    query = request.GET.get('q', '').strip()
    sort_key = request.GET.get('sort', 'new')
    series = Series.objects.filter(is_active=True).prefetch_related('genres')
    series = _apply_catalog_filters(series, query, sort_key)
    paginator = Paginator(series, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'movies/series.html',
        {
            'series': page_obj,
            'page_obj': page_obj,
            'query': query,
            'sort': sort_key,
            'page_title': 'Каталог сериалов',
        },
    )


def series_detail(request, series_id, slug=None):
    """Детальная страница сериала"""
    # Получаем сериал по ID или показываем 404
    series = get_object_or_404(
        Series.objects.prefetch_related(
            'genres',
            Prefetch('reviews', queryset=SeriesReview.objects.filter(is_active=True)),
        ),
        id=series_id,
        is_active=True,
    )
    if not series.slug:
        series.save()
    if slug is None or slug != series.slug:
        return redirect('movies:detail_series', series_id=series.id, slug=series.slug)

    increment_view = request.method == 'GET'
    view_cookie = f"viewed_series_{series.id}"
    if increment_view and not request.COOKIES.get(view_cookie):
        Series.objects.filter(pk=series.pk).update(views=F('views') + 1)
        series.refresh_from_db(fields=['views'])

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteSeries.objects.filter(user=request.user, series=series).exists()

    reviews = series.reviews.all()
    form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            SeriesReview.objects.create(
                series=series,
                user=request.user,
                rating=form.cleaned_data['rating'],
                text=form.cleaned_data['text'],
            )
            messages.success(request, 'Отзыв добавлен.')
            return redirect('movies:detail_series', series_id=series.id, slug=series.slug)

    similar_items = (
        Series.objects.filter(is_active=True, genres__in=series.genres.all())
        .exclude(id=series.id)
        .distinct()
        .order_by('-rating')[:10]
    )

    context = {
        'series': series,
        'page_title': series.title,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'review_form': form,
        'similar_items': similar_items,
    }
    response = render(request, 'movies/detail_series.html', context)
    if increment_view and not request.COOKIES.get(view_cookie):
        response.set_cookie(view_cookie, 'true', max_age=60 * 60 * 24 * 30, path='/')
    return response


def shows_list(request):
    query = request.GET.get('q', '').strip()
    sort_key = request.GET.get('sort', 'new')
    shows = Show.objects.filter(is_active=True).prefetch_related('genres')
    shows = _apply_catalog_filters(shows, query, sort_key)
    paginator = Paginator(shows, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'movies/shows.html',
        {
            'shows': page_obj,
            'page_obj': page_obj,
            'query': query,
            'sort': sort_key,
            'page_title': 'Каталог шоу',
        },
    )


def show_detail(request, show_id, slug=None):
    show = get_object_or_404(
        Show.objects.prefetch_related(
            'genres',
            Prefetch('reviews', queryset=ShowReview.objects.filter(is_active=True)),
        ),
        id=show_id,
        is_active=True,
    )
    if not show.slug:
        show.save()
    if slug is None or slug != show.slug:
        return redirect('movies:detail_show', show_id=show.id, slug=show.slug)

    increment_view = request.method == 'GET'
    view_cookie = f"viewed_show_{show.id}"
    if increment_view and not request.COOKIES.get(view_cookie):
        Show.objects.filter(pk=show.pk).update(views=F('views') + 1)
        show.refresh_from_db(fields=['views'])

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteShow.objects.filter(user=request.user, show=show).exists()

    reviews = show.reviews.all()
    form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            ShowReview.objects.create(
                show=show,
                user=request.user,
                rating=form.cleaned_data['rating'],
                text=form.cleaned_data['text'],
            )
            messages.success(request, 'Отзыв добавлен.')
            return redirect('movies:detail_show', show_id=show.id, slug=show.slug)

    similar_items = (
        Show.objects.filter(is_active=True, genres__in=show.genres.all())
        .exclude(id=show.id)
        .distinct()
        .order_by('-rating')[:10]
    )

    context = {
        'show': show,
        'page_title': show.title,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'review_form': form,
        'similar_items': similar_items,
    }
    response = render(request, 'movies/detail_show.html', context)
    if increment_view and not request.COOKIES.get(view_cookie):
        response.set_cookie(view_cookie, 'true', max_age=60 * 60 * 24 * 30, path='/')
    return response


def show_watch(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    if show.video_url:
        return redirect(show.video_url)
    return render(request, 'movies/not_available.html', {'obj': show, 'type': 'шоу'})


def show_watch_trailer(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    if show.trailer_url:
        return redirect(show.trailer_url)
    return render(request, 'movies/not_available.html', {'obj': show, 'type': 'шоу'})


@login_required
def toggle_favorite_show(request, show_id):
    show = get_object_or_404(Show, id=show_id, is_active=True)
    favorite, created = FavoriteShow.objects.get_or_create(user=request.user, show=show)
    if not created:
        favorite.delete()
        messages.info(request, 'Удалено из избранного.')
    else:
        messages.success(request, 'Добавлено в избранное.')
    return redirect('movies:detail_show', show_id=show.id, slug=show.slug)

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


@login_required
def toggle_favorite_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id, is_active=True)
    favorite, created = FavoriteMovie.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        favorite.delete()
        messages.info(request, 'Удалено из избранного.')
    else:
        messages.success(request, 'Добавлено в избранное.')
    return redirect('movies:detail', movie_id=movie.id, slug=movie.slug)


@login_required
def toggle_favorite_series(request, series_id):
    series = get_object_or_404(Series, id=series_id, is_active=True)
    favorite, created = FavoriteSeries.objects.get_or_create(user=request.user, series=series)
    if not created:
        favorite.delete()
        messages.info(request, 'Удалено из избранного.')
    else:
        messages.success(request, 'Добавлено в избранное.')
    return redirect('movies:detail_series', series_id=series.id, slug=series.slug)

#О нас
def about(request):
    """Страница О нас"""
    context = {
        'page_title': 'О компании RV КИНО'
    }
    return render(request, 'movies/about.html', context)


def news_list(request):
    """Список новостей"""
    news_qs = News.objects.filter(is_published=True, published_at__lte=timezone.now())
    paginator = Paginator(news_qs, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'news_list': page_obj,
        'page_obj': page_obj,
        'page_title': 'Новости',
    }
    return render(request, 'movies/news_list.html', context)


def news_detail(request, news_id, slug=None):
    """Детальная страница новости"""
    news_item = get_object_or_404(
        News, id=news_id, is_published=True, published_at__lte=timezone.now()
    )
    if slug is None or slug != news_item.slug:
        return redirect('movies:news_detail', news_id=news_item.id, slug=news_item.slug)

    context = {
        'news_item': news_item,
        'page_title': news_item.title,
    }
    return render(request, 'movies/news_detail.html', context)


def community_detail(request, community_id):
    """Детальная страница сообщества"""
    community = get_object_or_404(
        Community.objects.select_related('created_by')
        .only('id', 'name', 'slug', 'description', 'members', 'contact_info', 'avatar', 'created_at', 'created_by__id', 'created_by__username')
        .prefetch_related('members_users'),
        id=community_id,
        is_active=True
    )
    
    # Получаем проекты сообщества через связующую модель
    community_projects = CommunityProject.objects.filter(community=community).select_related(
        'movie', 'series', 'show'
    )
    
    # Формируем список проектов
    projects = []
    for comm_project in community_projects:
        if comm_project.movie:
            projects.append({
                'kind': 'movie',
                'id': comm_project.movie.id,
                'slug': comm_project.movie.slug,
                'title': comm_project.movie.title,
                'poster': comm_project.movie.poster.url if comm_project.movie.poster else '',
                'rating': comm_project.movie.rating,
                'year': comm_project.movie.year,
                'views': comm_project.movie.views,
            })
        elif comm_project.series:
            projects.append({
                'kind': 'series',
                'id': comm_project.series.id,
                'slug': comm_project.series.slug,
                'title': comm_project.series.title,
                'poster': comm_project.series.poster.url if comm_project.series.poster else '',
                'rating': comm_project.series.rating,
                'year': comm_project.series.year,
                'views': comm_project.series.views,
            })
        elif comm_project.show:
            projects.append({
                'kind': 'show',
                'id': comm_project.show.id,
                'slug': comm_project.show.slug,
                'title': comm_project.show.title,
                'poster': comm_project.show.poster.url if comm_project.show.poster else '',
                'rating': comm_project.show.rating,
                'year': comm_project.show.year,
                'views': comm_project.show.views,
            })
    
    members_with_roles = list(
        CommunityMembership.objects.filter(community=community)
        .select_related('user', 'user__profile')
        .order_by('-role', 'user__username')
    )

    context = {
        'community': community,
        'projects': projects,
        'members_with_roles': members_with_roles,
        'page_title': community.name,
    }
    return render(request, 'movies/community_detail.html', context)