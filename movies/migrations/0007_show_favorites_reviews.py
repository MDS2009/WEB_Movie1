from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_heroslide'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Show',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('slug', models.SlugField(blank=True, max_length=220, null=True, unique=True, verbose_name='Слаг')),
                ('description', models.TextField(verbose_name='Описание')),
                ('poster', models.ImageField(blank=True, null=True, upload_to='posters/', verbose_name='Постер')),
                ('year', models.IntegerField(default=2024, verbose_name='Год выпуска')),
                ('rating', models.DecimalField(decimal_places=1, default=0.0, max_digits=3, verbose_name='Рейтинг')),
                ('duration', models.IntegerField(default=0, verbose_name='Длительность (минуты)')),
                ('views', models.IntegerField(db_index=True, default=0, verbose_name='Просмотры')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('video_url', models.URLField(blank=True, null=True, verbose_name='Ссылка на видео')),
                ('trailer_url', models.URLField(blank=True, null=True, verbose_name='Ссылка на трейлер')),
                ('age_rating', models.CharField(blank=True, max_length=10, null=True, verbose_name='Возраст')),
                ('actors', models.CharField(blank=True, max_length=500, null=True, verbose_name='Актёры')),
                ('director', models.CharField(blank=True, max_length=200, null=True, verbose_name='Режиссёр')),
                ('producer', models.CharField(blank=True, max_length=200, null=True, verbose_name='Продюсер')),
            ],
            options={
                'verbose_name': 'Шоу',
                'verbose_name_plural': 'Шоу',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ShowReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(verbose_name='Оценка')),
                ('text', models.TextField(verbose_name='Отзыв')),
                ('is_active', models.BooleanField(default=True, verbose_name='Опубликован')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='movies.show')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Отзыв о шоу',
                'verbose_name_plural': 'Отзывы о шоу',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FavoriteShow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='movies.show')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Избранное шоу',
                'verbose_name_plural': 'Избранные шоу',
            },
        ),
        migrations.AddField(
            model_name='show',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='shows', to='movies.genre', verbose_name='Жанры'),
        ),
        migrations.AddIndex(
            model_name='show',
            index=models.Index(fields=['is_active'], name='movies_show_is_acti_8b7c2b_idx'),
        ),
        migrations.AddIndex(
            model_name='show',
            index=models.Index(fields=['year'], name='movies_show_year_4e97e9_idx'),
        ),
        migrations.AddIndex(
            model_name='show',
            index=models.Index(fields=['rating'], name='movies_show_rating_f38f9f_idx'),
        ),
        migrations.AddIndex(
            model_name='showreview',
            index=models.Index(fields=['show', 'is_active'], name='movies_show_show_i_4d32a0_idx'),
        ),
        migrations.AddIndex(
            model_name='favoriteshow',
            index=models.Index(fields=['user', 'show'], name='movies_favo_user_id_e9db18_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='favoriteshow',
            unique_together={('user', 'show')},
        ),
    ]
