# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import socket

from typing import Any, Dict, List

from django.urls import reverse_lazy

from configurations import Configuration, values


class Base(Configuration):

    SECRET_KEY = values.SecretValue()
    DATABASES = values.DatabaseURLValue()
    REDIS_URL = values.Value(environ_name="REDIS_URL", environ_prefix=None)

    ATOMIC_REQUESTS = True

    EMAIL_HOST = values.Value()
    EMAIL_PORT = values.PositiveIntegerValue()

    EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"

    DEBUG = False
    ALLOWED_HOSTS: List[str] = []

    WSGI_APPLICATION = "communikit.wsgi.application"

    DJANGO_APPS = [
        "django.forms",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.messages",
        "django.contrib.postgres",
        "django.contrib.staticfiles",
    ]

    THIRD_PARTY_APPS = [
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        "djcelery_email",
        "markdownx",
        "micawber.contrib.mcdjango",
        "rules.apps.AutodiscoverRulesConfig",
        "sorl.thumbnail",
        "widget_tweaks",
    ]

    LOCAL_APPS = [
        "communikit.activities.apps.ActivitiesConfig",
        "communikit.comments.apps.CommentsConfig",
        "communikit.communities.apps.CommunitiesConfig",
        "communikit.core.apps.CoreConfig",
        "communikit.events.apps.EventsConfig",
        "communikit.invites.apps.InvitesConfig",
        "communikit.join_requests.apps.JoinRequestsConfig",
        "communikit.notifications.apps.NotificationsConfig",
        "communikit.photos.apps.PhotosConfig",
        "communikit.posts.apps.PostsConfig",
        "communikit.users.apps.UsersConfig",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sites.middleware.CurrentSiteMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "communikit.core.turbolinks.middleware.TurbolinksMiddleware",
        "communikit.communities.middleware.CurrentCommunityMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "communikit.urls"

    # project-specific

    DEFAULT_PAGE_SIZE = 12

    HOME_PAGE_URL = reverse_lazy("activities:stream")

    AUTH_USER_MODEL = "users.User"

    # https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
    AUTHENTICATION_BACKENDS = [
        "rules.permissions.ObjectPermissionBackend",
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    ]

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"  # noqa
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"  # noqa
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"  # noqa
        },
    ]

    LOGIN_URL = "account_login"
    LOGIN_REDIRECT_URL = HOME_PAGE_URL

    ACCOUNT_EMAIL_REQUIRED = True

    SITE_ID = 1

    # Internationalization
    # https://docs.djangoproject.com/en/2.2/topics/i18n/

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.2/howto/static-files/

    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"

    # https://docs.djangoproject.com/en/1.11/ref/forms/renderers/

    FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

    # https://neutronx.github.io/django-markdownx/customization/

    MARKDOWNX_MARKDOWNIFY_FUNCTION = (
        "communikit.core.markdown.utils.markdownify"
    )

    # https://micawber.readthedocs.io/en/latest/django.html
    MICAWBER_PROVIDERS = "communikit.activities.oembed.bootstrap_oembed"

    # https://celery.readthedocs.io/en/latest/userguide/configuration.html

    CELERY_RESULT_BACKEND = CELERY_BROKER_URL = REDIS_URL
    CELERY_TASK_SERIALIZER = CELERY_RESULT_SERIALIZER = "json"

    @property
    def BASE_DIR(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def INSTALLED_APPS(self) -> List[str]:
        return self.DJANGO_APPS + self.THIRD_PARTY_APPS + self.LOCAL_APPS

    @property
    def MEDIA_ROOT(self) -> str:
        return os.path.join(self.BASE_DIR, "media")

    @property
    def STATIC_ROOT(self) -> str:
        return os.path.join(self.BASE_DIR, "static")

    @property
    def STATICFILES_DIRS(self) -> List[str]:
        return [os.path.join(self.BASE_DIR, "assets")]

    @property
    def TEMPLATES(self) -> List[Dict]:
        return [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [os.path.join(self.BASE_DIR, "templates")],
                "APP_DIRS": True,
                "OPTIONS": {
                    "debug": self.DEBUG,
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.template.context_processors.i18n",
                        "django.template.context_processors.media",
                        "django.template.context_processors.static",
                        "django.template.context_processors.tz",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            }
        ]

    # Sorl-thumbnail

    @property
    def THUMBNAIL_DEBUG(self) -> bool:
        return self.DEBUG

    @property
    def CACHES(self) -> Dict[str, Any]:
        return {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": self.REDIS_URL,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient"
                },
            }
        }


class DockerConfigMixin:
    @property
    def INTERNAL_IPS(self) -> List[str]:
        ips = ["127.0.0.1", "10.0.2.2"]
        _, _, ips = socket.gethostbyname_ex(socket.gethostname())
        ips += [ip[:-1] + "1" for ip in ips]
        return ips


class Testing(Base):
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    ALLOWED_HOSTS = Configuration.ALLOWED_HOSTS + [".example.com"]
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }


class Local(DockerConfigMixin, Base):
    DEBUG = True
    THIRD_PARTY_APPS = Base.THIRD_PARTY_APPS + [
        "debug_toolbar",
        "django_extensions",
    ]

    MIDDLEWARE = Base.MIDDLEWARE + [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
        "SHOW_TEMPLATE_CONTEXT": True,
    }


class Production(DockerConfigMixin, Base):

    THIRD_PARTY_APPS = Base.THIRD_PARTY_APPS + ["anymail"]

    ALLOWED_HOSTS = values.ListValue()
    ADMINS = values.ListValue()

    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    DEFAULT_FILE_STORAGE = "communikit.core.storages.MediaStorage"
    STATICFILES_STORAGE = "communikit.core.storages.StaticStorage"

    AWS_MEDIA_LOCATION = "media"
    AWS_STATIC_LOCATION = "static"

    AWS_ACCESS_KEY_ID = values.Value()
    AWS_SECRET_ACCESS_KEY = values.Value()
    AWS_STORAGE_BUCKET_NAME = values.Value()
    AWS_S3_REGION_NAME = values.Value("eu-north-1")
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = "public-read"

    CELERY_EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    MAILGUN_API_KEY = values.Value()
    MAILGUN_SENDER_DOMAIN = values.Value()

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {"django": {"handlers": ["console"], "level": "INFO"}},
    }

    @property
    def s3_url(self) -> str:
        return (
            f"https://{self.AWS_STORAGE_BUCKET_NAME}."
            f"s3.{self.AWS_S3_REGION_NAME}.amazonaws.com/"
        )

    @property
    def MEDIA_URL(self) -> str:
        return f"{self.s3_url}{self.AWS_MEDIA_LOCATION}/"

    @property
    def STATIC_URL(self) -> str:
        return f"{self.s3_url}{self.AWS_STATIC_LOCATION}/"

    @property
    def ANYMAIL(self) -> Dict[str, str]:
        return {
            "MAILGUN_API_KEY": self.MAILGUN_API_KEY,
            "MAILGUN_SENDER_DOMAIN": self.MAILGUN_SENDER_DOMAIN,
        }

    @property
    def SERVER_EMAIL(self) -> str:
        return f"errors@{self.MAILGUN_SENDER_DOMAIN}"

    @property
    def DEFAULT_FROM_EMAIL(self) -> str:
        return f"support@{self.MAILGUN_SENDER_DOMAIN}"
