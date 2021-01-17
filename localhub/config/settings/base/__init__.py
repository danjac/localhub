# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import pathlib
import socket
from email.utils import getaddresses

# Django
from django.contrib import messages
from django.urls import reverse_lazy

# Third Party Libraries
import environ
import pymdownx
import pymdownx.emoji

env = environ.Env()

DEBUG = False

BASE_DIR = pathlib.Path("/app")

SECRET_KEY = env("SECRET_KEY")

DATABASES = {
    "default": env.db(),
}

REDIS_URL = env("REDIS_URL")

CACHES = {"default": env.cache("REDIS_URL")}

EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"

ATOMIC_REQUESTS = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# configure internal IPS inside docker container

INTERNAL_IPS = [
    ip[:-1] + "1" for ip in socket.gethostbyname_ex(socket.gethostname())[2]
]

ADMINS = getaddresses(env.list("ADMINS", default=[]))

SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN", default=None)
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN", default=None)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

ROOT_URLCONF = "localhub.config.urls"
WSGI_APPLICATION = "localhub.config.wsgi.application"

LOCAL_APPS = [
    "localhub.activities.apps.ActivitiesConfig",
    "localhub.activities.events.apps.EventsConfig",
    "localhub.activities.photos.apps.PhotosConfig",
    "localhub.activities.polls.apps.PollsConfig",
    "localhub.activities.posts.apps.PostsConfig",
    "localhub.bookmarks.apps.BookmarksConfig",
    "localhub.comments.apps.CommentsConfig",
    "localhub.communities.apps.CommunitiesConfig",
    "localhub.flags.apps.FlagsConfig",
    "localhub.hashtags.apps.HashtagsConfig",
    "localhub.invites.apps.InvitesConfig",
    "localhub.join_requests.apps.JoinRequestsConfig",
    "localhub.likes.apps.LikesConfig",
    "localhub.notifications.apps.NotificationsConfig",
    "localhub.private_messages.apps.PrivateMessagesConfig",
    "localhub.users.apps.UsersConfig",
]


INSTALLED_APPS = [
    "django.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django_extensions",
    "djcelery_email",
    "markdownx",
    "micawber.contrib.mcdjango",
    "rules.apps.AutodiscoverRulesConfig",
    "sorl.thumbnail",
    "taggit",
    "widget_tweaks",
] + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "turbo_response.middleware.TurboStreamMiddleware",
    "localhub.common.middleware.search.SearchMiddleware",
    "localhub.communities.middleware.CurrentCommunityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "localhub.users.middleware.UserLocaleMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "localhub.common.middleware.http.HttpResponseNotAllowedMiddleware",
]

DEFAULT_PAGE_SIZE = 12
LONG_PAGE_SIZE = 24

HOME_PAGE_URL = reverse_lazy("activity_stream")

# base Django admin URL (should be something obscure in production)

ADMIN_URL = env("ADMIN_URL", default="admin/")

# sorl

THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.redis_kvstore.KVStore"
THUMBNAIL_REDIS_URL = REDIS_URL
THUMBNAIL_DEBUG = False

# auth

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
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = HOME_PAGE_URL

ACCOUNT_USER_DISPLAY = "localhub.users.utils.user_display"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

SOCIALACCOUNT_ADAPTER = "localhub.users.adapters.SocialAccountAdapter"

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English (US)"),
    ("en-gb", "English (GB)"),
    ("fi", "Suomi"),
]
LANGUAGE_COOKIE_DOMAIN = env("LANGUAGE_COOKIE_DOMAIN", default=None)
LANGUAGE_COOKIE_SAMESITE = "Lax"

LOCALE_PATHS = [BASE_DIR / "i18n"]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# https://docs.djangoproject.com/en/1.11/ref/forms/renderers/

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# https://docs.djangoproject.com/en/3.0/ref/contrib/messages/

MESSAGE_TAGS = {
    messages.DEBUG: "message-debug",
    messages.INFO: "message-info",
    messages.SUCCESS: "message-success",
    messages.WARNING: "message-warning",
    messages.ERROR: "message-error",
}

# https://neutronx.github.io/django-markdownx/customization/

MARKDOWNX_MARKDOWNIFY_FUNCTION = "localhub.common.markdown.utils.markdownify"

MARKDOWNX_MARKDOWN_EXTENSIONS = [
    "pymdownx.extra",
    "pymdownx.emoji",
    "codehilite",
    "localhub.common.markdown.extensions:NewTabExtension",
    "localhub.common.markdown.extensions:SafeImageExtension",
]

MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
    "pymdownx.emoji": {
        "emoji_generator": pymdownx.emoji.to_alt,
        "emoji_index": pymdownx.emoji.twemoji,
    }
}

# https://micawber.readthedocs.io/en/latest/django.html
MICAWBER_PROVIDERS = "localhub.activities.oembed.bootstrap_oembed"
MICAWBER_TEMPLATE_EXTENSIONS = [("oembed_no_urlize", {"urlize_all": False})]

# https://celery.readthedocs.io/en/latest/userguide/configuration.html
result_backend = CELERY_BROKER_URL = REDIS_URL
result_serializer = "json"

# https://django-taggit.readthedocs.io/en/latest/getting_started.html

TAGGIT_CASE_INSENSITIVE = True

# https://web-push-codelab.glitch.me/

VAPID_PUBLIC_KEY = env("VAPID_PUBLIC_KEY", default=None)
VAPID_PRIVATE_KEY = env("VAPID_PRIVATE_KEY", default=None)
VAPID_ADMIN_EMAIL = env("VAPID_ADMIN_EMAIL", default=None)

WEBPUSH_ENABLED = env.bool("WEBPUSH_ENABLED", default=True)

GEOLOCATOR_USER_AGENT = env("GEOLOCATOR_USER_AGENT", default="localhub.locator")

MEDIA_URL = env("MEDIA_URL", default="/media/")
STATIC_URL = env("STATIC_URL", default="/static/")

MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_DIRS = [BASE_DIR / "static"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": False,
            "builtins": [
                "localhub.common.template.defaultfilters",
                "localhub.common.template.defaulttags",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "localhub.communities.context_processors.community",
                "localhub.common.template.context_processors.search",
                "localhub.common.template.context_processors.home_page_url",
                "localhub.common.template.context_processors.is_cookies_accepted",
            ],
            "libraries": {"pagination": "localhub.common.pagination.templatetags"},
        },
    }
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
    },
    "loggers": {
        "root": {"handlers": ["console"], "level": "INFO"},
        "django.security.DisallowedHost": {"handlers": ["null"], "propagate": False},
        "django.request": {"handlers": ["console"], "level": "ERROR"},
        "localhub.activities.photos.forms": {"handlers": ["console"], "level": "INFO"},
        "localhub.notifications.adapter": {"handlers": ["console"], "level": "INFO"},
        "localhub.notifications.tasks": {"handlers": ["console"], "level": "INFO"},
    },
}
