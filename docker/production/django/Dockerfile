FROM python:3.7-alpine
MAINTAINER danjac2018@gmail.com

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk update \
      && apk add --virtual build-deps gcc python3-dev musl-dev \
      && apk add postgresql-dev \
      && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
      && apk add libffi-dev py-cffi \
      && apk add gettext \
      && apk add postgresql-client

RUN pip install -U pip

# Copy requirements to insure caching
COPY ./requirements /requirements

RUN pip install -r /requirements/production.txt

WORKDIR /app

RUN adduser -D communikit_user
USER communikit_user

COPY ./docker/local/django/entrypoint /app/entrypoint
RUN chmod +x /app/entrypoint

COPY ./docker/local/django/start-django /app/start-django
RUN chmod +x /app/start-django

COPY ./docker/local/django/start-celeryworker /app/start-celeryworker
RUN chmod +x /app/start-celeryworker

COPY ./docker/local/django/start-celerybeat /app/start-celerybeat
RUN chmod +x /app/start-celerybeat

COPY ./docker/local/django/start-flower /app/start-flower
RUN chmod +x /app/start-flower

ENTRYPOINT ["/app/entrypoint"]
