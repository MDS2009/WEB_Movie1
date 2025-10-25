
from django.db import models

# Модель для фильма
class Movie(models.Model):
    # Основная информация
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    poster = models.ImageField('Постер', upload_to='posters/', blank=True, null=True)

    # Рейтинги
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, default=0.0)

    # Детали
    year = models.IntegerField('Год выпуска', default=2024)
    duration = models.IntegerField('Длительность (минуты)', default=0)

    # Счётчики
    views = models.IntegerField('Просмотры', default=0)

    # Системные поля
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']  # Новые фильмы первыми

    def __str__(self):
        return self.title