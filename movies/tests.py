from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Movie, Series, Genre, FavoriteMovie, MovieReview


class MoviesSmokeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            email='tester@example.com',
            password='password123',
        )
        self.genre = Genre.objects.create(name='Драма')
        self.movie = Movie.objects.create(
            title='Тестовый фильм',
            description='Описание',
            year=2024,
            rating=8.5,
            duration=120,
            is_active=True,
        )
        self.movie.genres.add(self.genre)
        self.series = Series.objects.create(
            title='Тестовый сериал',
            description='Описание',
            year=2023,
            rating=7.1,
            duration=45,
            is_active=True,
        )

    def test_index_page(self):
        response = self.client.get(reverse('movies:index'))
        self.assertEqual(response.status_code, 200)

    def test_movies_list_search_sort(self):
        Movie.objects.create(
            title='Альфа',
            description='Поиск',
            year=2022,
            rating=9.0,
            duration=110,
            is_active=True,
        )
        response = self.client.get(reverse('movies:films'), {'q': 'Альфа', 'sort': 'rating'})
        self.assertEqual(response.status_code, 200)
        movies = list(response.context['movies'])
        self.assertTrue(any(m.title == 'Альфа' for m in movies))

    def test_movies_list_pagination(self):
        for i in range(15):
            Movie.objects.create(
                title=f'Фильм {i}',
                description='Описание',
                year=2020 + i,
                rating=5.0,
                duration=90,
                is_active=True,
            )
        response = self.client.get(reverse('movies:films'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_previous())

    def test_movie_detail_slug_redirect(self):
        response = self.client.get(reverse('movies:detail', args=[self.movie.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.movie.slug, response['Location'])

    def test_movie_review_and_favorite(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('movies:detail', args=[self.movie.id, self.movie.slug]),
            {'rating': 8, 'text': 'Отличный фильм'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MovieReview.objects.filter(movie=self.movie, user=self.user).exists())

        response = self.client.get(reverse('movies:favorite_movie', args=[self.movie.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(FavoriteMovie.objects.filter(movie=self.movie, user=self.user).exists())
