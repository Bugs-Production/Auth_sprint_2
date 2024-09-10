# Generated by Django 4.2.11 on 2024-06-22 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_filmwork_file_path'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='genrefilmwork',
            unique_together={('genre', 'film_work')},
        ),
        migrations.AlterUniqueTogether(
            name='personfilmwork',
            unique_together={('film_work', 'person', 'role')},
        ),
    ]
