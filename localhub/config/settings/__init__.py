# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later
# Standard Library
import logging

# Third Party Libraries
from configurations import values

# Local
from .base import Base
from .mixins import AWSMixin, DockerMixin, MailgunMixin


class Testing(Base):
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

    ALLOWED_HOSTS = Base.ALLOWED_HOSTS + [".example.com"]

    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

    THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.cached_db_kvstore.KVStore"

    SITE_ID = 1

    THIRD_PARTY_APPS = Base.THIRD_PARTY_APPS + [
        "nplusone.ext.django",
    ]

    NPLUSONE_RAISE = True


class Local(DockerMixin, Base):

    DEBUG = True

    ALLOWED_HOSTS = ["*"]

    THIRD_PARTY_APPS = Base.THIRD_PARTY_APPS + [
        "debug_toolbar",
        "nplusone.ext.django",
    ]

    MIDDLEWARE = Base.MIDDLEWARE + [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "nplusone.ext.django.NPlusOneMiddleware",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
        "SHOW_TEMPLATE_CONTEXT": True,
    }

    SITE_ID = 1

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {
            "root": {"handlers": ["console"], "level": "DEBUG"},
            "nplusone": {"handlers": ["console"], "level": "WARN"},
        },
    }


class Production(Base):
    """
    Production settings for 12-factor deployment using environment variables.
    """

    ALLOWED_HOSTS = values.ListValue()
    CSRF_TRUSTED_ORIGINS = values.ListValue()

    ADMINS = values.SingleNestedTupleValue()

    # Security settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 15768001  # 6 months
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    MIDDLEWARE = Base.MIDDLEWARE + [
        "localhub.middleware.http.HttpResponseNotAllowedMiddleware",
    ]

    NPLUSONE_LOGGER = logging.getLogger("nplusone")
    NPLUSONE_LOG_LEVEL = logging.WARN

    @property
    def LOGGING(self):
        logging = super().LOGGING
        logging["loggers"]["nplusone"] = {"handlers": ["console"], "level": "WARN"}
        return logging


class Deployment(AWSMixin, Production):
    """Settings for running tasks in the deployment pipeline."""


class Heroku(DockerMixin, AWSMixin, MailgunMixin, Production):
    """
    Production settings specific to Heroku docker-based setup.

    See heroku.yml for additional settings.
    """

    # This is required for Heroku SSL.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
