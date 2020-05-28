# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import socket

# Third Party Libraries
from configurations import values


class DockerMixin:
    """Configuration for Docker deployments."""

    @property
    def INTERNAL_IPS(self):
        _, _, ips = socket.gethostbyname_ex(socket.gethostname())
        return [ip[:-1] + "1" for ip in ips]


class MailgunMixin:
    """Configuration for Mailgun email"""

    CELERY_EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    MAILGUN_API_KEY = values.Value()
    MAILGUN_SENDER_DOMAIN = values.Value()

    @property
    def ANYMAIL(self):
        return {
            "MAILGUN_API_KEY": self.MAILGUN_API_KEY,
            "MAILGUN_SENDER_DOMAIN": self.MAILGUN_SENDER_DOMAIN,
        }

    @property
    def SERVER_EMAIL(self):
        return f"errors@{self.MAILGUN_SENDER_DOMAIN}"

    @property
    def DEFAULT_FROM_EMAIL(self):
        return f"support@{self.MAILGUN_SENDER_DOMAIN}"

    @property
    def INSTALLED_APPS(self):
        return super().INSTALLED_APPS + ["anymail"]


class AWSMixin:
    """Configuration for S3 deployments.
    """

    DEFAULT_FILE_STORAGE = "social_bfg.config.storages.MediaStorage"
    STATICFILES_STORAGE = "social_bfg.config.storages.StaticStorage"

    AWS_MEDIA_LOCATION = "media"
    AWS_STATIC_LOCATION = "static"

    AWS_ACCESS_KEY_ID = values.Value()
    AWS_SECRET_ACCESS_KEY = values.Value()
    AWS_STORAGE_BUCKET_NAME = values.Value()
    AWS_S3_CUSTOM_DOMAIN = values.Value()
    AWS_S3_REGION_NAME = values.Value("eu-north-1")
    AWS_QUERYSTRING_AUTH = False
    AWS_IS_GZIPPED = True
    AWS_DEFAULT_ACL = "public-read"

    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=600"}
