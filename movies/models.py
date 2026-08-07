from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify


def _generate_unique_slug(model, base_slug):
    slug = base_slug
    suffix = 1
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug


class CommunityProject(models.Model):
    """Связь между сообществом и проектами"""
    community = models.ForeignKey('users.Community', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, blank=True, null=True)
    series = models.ForeignKey('Series', on_delete=models.CASCADE, blank=True, null=True)
    show = models.ForeignKey('Show', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Проект сообщества'
        verbose_name_plural = 'Проекты сообществ'
        constraints = [
            models.CheckConstraint(
                check=models.Q(movie__isnull=False) | models.Q(series__isnull=False) | models.Q(show__isnull=False),
                name='at_least_one_project'
            )
        ]

    def __str__(self):
        if self.movie:
            return f"{self.community} → {self.movie}"
        elif self.series:
            return f"{self.community} → {self.series}"
        elif self.show:
            return f"{self.community} → {self.show}"
        return f"{self.community} → Неизвестный проект"


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=100, unique=True)
    slug = models.SlugField('Слаг', max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'genre'
            self.slug = _generate_unique_slug(Genre, base_slug)
        super().save(*args, **kwargs)


class Movie(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=220, unique=True, blank=True, null=True)
    description = models.TextField('Описание')
    poster = models.ImageField('Постер', upload_to='posters/', blank=True, null=True)
    year = models.IntegerField('Год выпуска', default=2024)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, default=0.0)
    duration = models.IntegerField('Длительность (минуты)', default=0)
    views = models.IntegerField('Просмотры', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    video_url = models.URLField('Ссылка на видео', blank=True, null=True)
    trailer_url = models.URLField('Ссылка на трейлер', blank=True, null=True)
    age_rating = models.CharField('Возраст', max_length=10, blank=True, null=True)
    actors = models.CharField('Актёры', max_length=500, blank=True, null=True)
    director = models.CharField('Режиссёр', max_length=200, blank=True, null=True)
    producer = models.CharField('Продюсер', max_length=200, blank=True, null=True)
    genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True, related_name='movies')

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['year']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'movie'
            self.slug = _generate_unique_slug(Movie, base_slug)
        super().save(*args, **kwargs)


class Series(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=220, unique=True, blank=True, null=True)
    description = models.TextField('Описание')
    poster = models.ImageField('Постер', upload_to='posters/', blank=True, null=True)
    year = models.IntegerField('Год выпуска', default=2024)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, default=0.0)
    duration = models.IntegerField('Длительность (минуты)', default=0)
    views = models.IntegerField('Просмотры', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    video_url = models.URLField('Ссылка на видео', blank=True, null=True)
    trailer_url = models.URLField('Ссылка на трейлер', blank=True, null=True)
    age_rating = models.CharField('Возраст', max_length=10, blank=True, null=True)
    actors = models.CharField('Актёры', max_length=500, blank=True, null=True)
    director = models.CharField('Режиссёр', max_length=200, blank=True, null=True)
    producer = models.CharField('Продюсер', max_length=200, blank=True, null=True)
    genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True, related_name='series')

    class Meta:
        verbose_name = 'Сериал'
        verbose_name_plural = 'Сериалы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['year']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'series'
            self.slug = _generate_unique_slug(Series, base_slug)
        super().save(*args, **kwargs)


class Show(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=220, unique=True, blank=True, null=True)
    description = models.TextField('Описание')
    poster = models.ImageField('Постер', upload_to='posters/', blank=True, null=True)
    year = models.IntegerField('Год выпуска', default=2024)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, default=0.0)
    duration = models.IntegerField('Длительность (минуты)', default=0)
    views = models.IntegerField('Просмотры', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    video_url = models.URLField('Ссылка на видео', blank=True, null=True)
    trailer_url = models.URLField('Ссылка на трейлер', blank=True, null=True)
    age_rating = models.CharField('Возраст', max_length=10, blank=True, null=True)
    actors = models.CharField('Актёры', max_length=500, blank=True, null=True)
    director = models.CharField('Режиссёр', max_length=200, blank=True, null=True)
    producer = models.CharField('Продюсер', max_length=200, blank=True, null=True)
    genres = models.ManyToManyField(Genre, verbose_name='Жанры', blank=True, related_name='shows')

    class Meta:
        verbose_name = 'Шоу'
        verbose_name_plural = 'Шоу'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['year']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'show'
            self.slug = _generate_unique_slug(Show, base_slug)
        super().save(*args, **kwargs)


class HeroSlide(models.Model):
    title = models.CharField('Заголовок', max_length=200, blank=True)
    poster = models.ImageField('Изображение', upload_to='hero/', blank=True, null=True)
    movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, blank=True, null=True)
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, blank=True, null=True)
    link_url = models.URLField('Ссылка', blank=True, null=True)
    is_active = models.BooleanField('Активен', default=True)
    sort_order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Слайд на главной'
        verbose_name_plural = 'Слайды на главной'
        ordering = ['sort_order', 'id']

    def __str__(self):
        if self.title:
            return self.title
        if self.movie:
            return str(self.movie)
        if self.series:
            return str(self.series)
        return f"Слайд {self.pk}"


class FavoriteMovie(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранный фильм'
        verbose_name_plural = 'Избранные фильмы'
        unique_together = ('user', 'movie')
        indexes = [models.Index(fields=['user', 'movie'])]

    def __str__(self):
        return f"{self.user} → {self.movie}"


class FavoriteSeries(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранный сериал'
        verbose_name_plural = 'Избранные сериалы'
        unique_together = ('user', 'series')
        indexes = [models.Index(fields=['user', 'series'])]

    def __str__(self):
        return f"{self.user} → {self.series}"


class FavoriteShow(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное шоу'
        verbose_name_plural = 'Избранные шоу'
        unique_together = ('user', 'show')
        indexes = [models.Index(fields=['user', 'show'])]

    def __str__(self):
        return f"{self.user} → {self.show}"


class MovieReview(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField('Оценка')
    text = models.TextField('Отзыв')
    is_active = models.BooleanField('Опубликован', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв о фильме'
        verbose_name_plural = 'Отзывы о фильмах'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['movie', 'is_active'])]

    def __str__(self):
        return f"{self.user} → {self.movie}"


class SeriesReview(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField('Оценка')
    text = models.TextField('Отзыв')
    is_active = models.BooleanField('Опубликован', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв о сериале'
        verbose_name_plural = 'Отзывы о сериалах'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['series', 'is_active'])]

    def __str__(self):
        return f"{self.user} → {self.series}"


class ShowReview(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField('Оценка')
    text = models.TextField('Отзыв')
    is_active = models.BooleanField('Опубликован', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв о шоу'
        verbose_name_plural = 'Отзывы о шоу'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['show', 'is_active'])]

    def __str__(self):
        return f"{self.user} → {self.show}"


class News(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('Слаг', max_length=255, unique=True, blank=True)
    content = models.TextField('Текст новости')
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    published_at = models.DateTimeField('Дата публикации', default=timezone.now)
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, blank=True, null=True, related_name='news_posts'
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(News, slugify(self.title) or 'news')
        super().save(*args, **kwargs)


def _recalculate_rating(parent, review_qs):
    """Пересчитывает средний рейтинг на основе опубликованных отзывов"""
    avg = review_qs.filter(is_active=True).aggregate(avg=Avg('rating'))['avg']
    new_rating = Decimal(str(avg)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP) if avg is not None else Decimal('0.0')
    if parent.rating != new_rating:
        parent.rating = new_rating
        parent.save(update_fields=['rating'])


@receiver(post_save, sender=MovieReview)
@receiver(post_delete, sender=MovieReview)
def update_movie_rating(sender, instance, **kwargs):
    _recalculate_rating(instance.movie, MovieReview.objects.filter(movie=instance.movie))


@receiver(post_save, sender=SeriesReview)
@receiver(post_delete, sender=SeriesReview)
def update_series_rating(sender, instance, **kwargs):
    _recalculate_rating(instance.series, SeriesReview.objects.filter(series=instance.series))


@receiver(post_save, sender=ShowReview)
@receiver(post_delete, sender=ShowReview)
def update_show_rating(sender, instance, **kwargs):
    _recalculate_rating(instance.show, ShowReview.objects.filter(show=instance.show))
