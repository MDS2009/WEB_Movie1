from decimal import Decimal, ROUND_HALF_UP

from django.db import migrations
from django.db.models import Avg


def recalc(apps, schema_editor):
    """
    Пересчитывает Movie/Series/Show.rating как среднее по опубликованным
    отзывам — раньше это поле не пересчитывалось автоматически и хранило
    произвольное вручную выставленное (или дефолтное 0.0) значение.
    """
    Movie = apps.get_model('movies', 'Movie')
    Series = apps.get_model('movies', 'Series')
    Show = apps.get_model('movies', 'Show')
    MovieReview = apps.get_model('movies', 'MovieReview')
    SeriesReview = apps.get_model('movies', 'SeriesReview')
    ShowReview = apps.get_model('movies', 'ShowReview')

    for model, review_model, fk in (
        (Movie, MovieReview, 'movie_id'),
        (Series, SeriesReview, 'series_id'),
        (Show, ShowReview, 'show_id'),
    ):
        ids_with_reviews = review_model.objects.filter(is_active=True).values_list(fk, flat=True).distinct()
        for obj_id in ids_with_reviews:
            avg = review_model.objects.filter(**{fk: obj_id, 'is_active': True}).aggregate(avg=Avg('rating'))['avg']
            if avg is None:
                continue
            new_rating = Decimal(str(avg)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
            model.objects.filter(id=obj_id).update(rating=new_rating)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0011_news'),
    ]

    operations = [
        migrations.RunPython(recalc, noop),
    ]
