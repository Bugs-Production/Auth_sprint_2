from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        "name",
        "description",
    )
    list_filter = ("name",)
    search_fields = (
        "name",
        "description",
    )


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_per_page = 20
    list_display = ("title", "type", "creation_date", "rating", "viewing_permission")
    list_filter = ("type", "rating", "viewing_permission")
    search_fields = ("title", "description", "id")
    ordering = ["title", "type"]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonFilmworkInline,)
    list_per_page = 20
    list_display = ("full_name",)
    search_fields = ("full_name",)
