#!/bin/bash

python manage.py migrate --fake --noinput
python manage.py collectstatic --no-input

uwsgi --strict --ini /app/uwsgi/uwsgi.ini
