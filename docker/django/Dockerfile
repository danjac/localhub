FROM python:3.7-alpine

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

RUN pip install -r /requirements/local.txt

WORKDIR /app

COPY ./docker/django/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/django/start-django /start-django
RUN chmod +x /start-django

COPY ./docker/django/start-celeryworker /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./docker/django/start-celerybeat /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./docker/django/start-flower /start-flower
RUN chmod +x /start-flower

ENTRYPOINT ["/entrypoint"]
