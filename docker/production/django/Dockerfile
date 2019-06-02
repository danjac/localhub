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

COPY ./docker/local/django/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/local/django/start-django /start-django
RUN chmod +x /start-django

COPY ./docker/local/django/start-celeryworker /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./docker/local/django/start-celerybeat /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./docker/local/django/start-flower /start-flower
RUN chmod +x /start-flower

ENTRYPOINT ["/entrypoint"]
