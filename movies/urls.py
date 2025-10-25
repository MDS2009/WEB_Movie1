from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('films/', views.movies_list, name='films'),
    path('movie/<int:movie_id>/', views.movie_detail, name='detail'),
    path('about/', views.about, name='about'),
]
