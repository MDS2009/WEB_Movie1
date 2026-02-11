from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_genre_moviereview_seriesreview_movie_slug_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Заголовок')),
                ('poster', models.ImageField(blank=True, null=True, upload_to='hero/', verbose_name='Изображение')),
                ('link_url', models.URLField(blank=True, null=True, verbose_name='Ссылка')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('movie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='movies.movie')),
                ('series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='movies.series')),
            ],
            options={
                'verbose_name': 'Слайд на главной',
                'verbose_name_plural': 'Слайды на главной',
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]
