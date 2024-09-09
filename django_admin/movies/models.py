import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class FilmTypeChoices(models.TextChoices):
    MOVIE = "movie", _("Movie")
    TV_SHOW = "tv_show", _("TV Show")


class RoleTypeChoices(models.TextChoices):
    ACTOR = "actor", _("Actor")
    DIRECTOR = "director", _("Director")
    WRITER = "writer", _("Writer")


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
    name = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("genre")
        verbose_name_plural = _("genres")

    def __str__(self):
        return self.name


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        unique_together = ["genre", "film_work"]
        verbose_name = _("genre-filmwork")
        verbose_name_plural = _("genre-filmworks")

    def __str__(self):
        return f"{self.film_work.title} - {self.genre.name}"


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_("full name"))

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("person")
        verbose_name_plural = _("persons")

    def __str__(self):
        return self.full_name


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=RoleTypeChoices.choices,
        default=RoleTypeChoices.ACTOR,
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        unique_together = ["film_work", "person", "role"]
        verbose_name = _("person-filmwork")
        verbose_name_plural = _("person-filmworks")

    def __str__(self):
        return f"{self.person.full_name} - {self.film_work.title}"


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_("title"), max_length=256)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateField(_("creation date"))
    rating = models.FloatField(_("rating"), validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(
        _("type"),
        max_length=20,
        choices=FilmTypeChoices.choices,
        default=FilmTypeChoices.MOVIE,
    )
    file_path = models.TextField(_('file path'), null=True, blank=True)
    genres = models.ManyToManyField(Genre, through="GenreFilmwork")
    persons = models.ManyToManyField(Person, through="PersonFilmwork")

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("filmwork")
        verbose_name_plural = _("filmworks")

    def __str__(self):
        return self.title
