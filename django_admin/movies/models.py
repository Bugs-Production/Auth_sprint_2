import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True,
                                   null=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class Types(models.TextChoices):
        MOVIE = "MV", _("movie")
        TV_SHOW = "TV", _("tv_show")

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True,
                                   null=True)
    creation_date = models.DateField(_('creation date'), blank=True, null=True)
    file_path = models.FileField(_('file'), blank=True, null=True,
                                 upload_to='movies/')
    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)], null=True)
    type = models.CharField(_('type'), max_length=255)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork', blank=True,
                                    null=True)
    persons = models.ManyToManyField('Person', through='PersonFilmwork',
                                     blank=True, null=True)

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('filmwork')
        verbose_name_plural = _('filmworks')
        indexes = [
            models.Index(fields=["creation_date"],
                         name="film_work_creation_date_idx"),
        ]

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        constraints = (
            models.UniqueConstraint(
                fields=['film_work', 'genre'],
                name='film_work_genre_idx'
            ),
        )


class Person(UUIDMixin, TimeStampedMixin):
    class Gender(models.TextChoices):
        MALE = 'male', _('male')
        FEMALE = 'female', _('female')

    full_name = models.CharField(_('full name'), max_length=255)
    gender = models.TextField(_('gender'), choices=Gender.choices,
                              null=True, blank=True)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('person')
        verbose_name_plural = _('persons')

    def __str__(self):
        return self.full_name


class PersonFilmwork(UUIDMixin):
    class Role(models.TextChoices):
        DIRECTOR = 'director', _('director')
        PRODUCER = 'producer', _('producer')
        ACTOR = 'actor', _('actor')
        SCREENWRITER = 'screenwriter', _('screenwriter')
        OPERATOR = 'operator', _('operator')
        COMPOSER = 'composer', _('composer')

    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.TextField(_('role'), choices=Role.choices,
                            null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        constraints = (
            models.UniqueConstraint(
                fields=['film_work', 'person', 'role'],
                name='film_work_person_idx'
            ),
        )

    def __str__(self):
        return self.film_work.title
