# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Local
from .base import *  # noqa
from .base import INSTALLED_APPS, MIDDLEWARE, TEMPLATES

DEBUG = True
THUMBNAIL_DEBUG = True
TEMPLATES[0]["OPTIONS"]["debug"] = True

SITE_ID = 1

INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS + ["silk"]

MIDDLEWARE = ["silk.middleware.SilkyMiddleware"] + MIDDLEWARE
