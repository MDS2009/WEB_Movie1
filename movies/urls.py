from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    
    path('films/', views.movies_list, name='films'),
    path('films/<int:movie_id>/watch/', views.movie_watch, name='movie_watch'),
    path('films/<int:movie_id>/trailer/', views.movie_watch_trailer, name='movie_watch_trailer'),
    path('films/<int:movie_id>/favorite/', views.toggle_favorite_movie, name='favorite_movie'),
    path('films/<int:movie_id>/', views.movie_detail, name='detail'),
    path('films/<int:movie_id>/<slug:slug>/', views.movie_detail, name='detail'),

    path('series/', views.series_list, name='series'),
    path('series/<int:series_id>/watch/', views.series_watch, name='series_watch'),
    path('series/<int:series_id>/trailer/', views.series_watch_trailer, name='series_watch_trailer'),
    path('series/<int:series_id>/favorite/', views.toggle_favorite_series, name='favorite_series'),
    path('series/<int:series_id>/', views.series_detail, name='detail_series'),
    path('series/<int:series_id>/<slug:slug>/', views.series_detail, name='detail_series'),

    path('shows/', views.shows_list, name='shows'),
    path('shows/<int:show_id>/watch/', views.show_watch, name='show_watch'),
    path('shows/<int:show_id>/trailer/', views.show_watch_trailer, name='show_watch_trailer'),
    path('shows/<int:show_id>/favorite/', views.toggle_favorite_show, name='favorite_show'),
    path('shows/<int:show_id>/', views.show_detail, name='detail_show'),
    path('shows/<int:show_id>/<slug:slug>/', views.show_detail, name='detail_show'),

    path('about/', views.about, name='about'),
    path('communities/<int:community_id>/', views.community_detail, name='community_detail'),
]