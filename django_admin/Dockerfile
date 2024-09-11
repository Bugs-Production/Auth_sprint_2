FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE=config.settings

RUN pip install --upgrade pip

RUN useradd -rms /bin/bash app && chmod 777 /opt /run

WORKDIR /app

RUN mkdir /app/static && mkdir /app/media && chown -R app:app /app && chmod 755 /app

COPY --chown=app:app . /app

RUN pip install -r requirements.txt

USER app

ENTRYPOINT ["sh", "./entrypoint.sh"]
