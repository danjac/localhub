# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "localhub.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

# from configurations.asgi import get_asgi_application  # noqa
# Use this until https://github.com/jazzband/django-configurations/pull/251 is merged
from configurations import importer  # isort:skip  # noqa


importer.install()

try:
    from django.core.asgi import get_asgi_application
except ImportError:  # pragma: no cover
    from django.core.handlers.asgi import ASGIHandler

    def get_asgi_application():  # noqa
        return ASGIHandler()


application = get_asgi_application()
