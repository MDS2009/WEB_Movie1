from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('films/', views.movies_list, name='films'),
    path('films/<int:movie_id>/', views.movie_detail, name='detail'),
    path('series/', views.series_list, name='series'),
    path('series/<int:series_id>/', views.series_detail, name='detail_series'),
    path('about/', views.about, name='about'),
    path('films/<int:movie_id>/watch/', views.movie_watch, name='movie_watch'),
    path('series/<int:series_id>/watch/', views.series_watch, name='series_watch'),
]