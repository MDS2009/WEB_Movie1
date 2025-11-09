from django.db import models


class Movie(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    poster = models.ImageField('Постер', upload_to='posters/', blank=True, null=True)
    year = models.IntegerField('Год выпуска', default=2024)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, default=0.0)
    duration = models.IntegerField('Длительность (минуты)', default=0)
    views = models.IntegerField('Просмотры', default=0)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Series(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    poster = models.ImageField('Постер', upload_to='posters/', blank=True, null=True)
    year = models.IntegerField('Год выпуска', default=2024)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, default=0.0)
    duration = models.IntegerField('Длительность (минуты)', default=0)
    views = models.IntegerField('Просмотры', default=0)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Сериал'
        verbose_name_plural = 'Сериалы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
