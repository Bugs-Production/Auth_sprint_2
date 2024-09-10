#!/bin/bash

python manage.py migrate --noinput
python manage.py collectstatic --no-input

uwsgi --strict --ini /app/uwsgi/uwsgi.ini
