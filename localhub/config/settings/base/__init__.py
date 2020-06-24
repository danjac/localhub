# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import socket
from email.utils import getaddresses

# Django
from django.contrib import messages

# Third Party Libraries
import environ
import pymdownx
import pymdownx.emoji

# Localhub
from localhub.config.app_settings import HOME_PAGE_URL

env = environ.Env()

root = environ.Path("/app")

DEBUG = False

SECRET_KEY = env("SECRET_KEY")

DATABASES = {
    "default": env.db(),
}

REDIS_URL = env.str("REDIS_URL")

CACHES = {"default": env.cache("REDIS_URL")}

EMAIL_HOST = env.str("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"

ATOMIC_REQUESTS = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# configure internal IPS inside docker container

INTERNAL_IPS = [
    ip[:-1] + "1" for ip in socket.gethostbyname_ex(socket.gethostname())[2]
]

ADMINS = getaddresses(env.list("ADMINS", default=[]))

SESSION_COOKIE_DOMAIN = env.str("SESSION_COOKIE_DOMAIN", default=None)
CSRF_COOKIE_DOMAIN = env.str("CSRF_COOKIE_DOMAIN", default=None)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

ROOT_URLCONF = "localhub.config.urls"
WSGI_APPLICATION = "localhub.config.wsgi.application"

LOCAL_APPS = [
    "localhub.apps.activities.apps.ActivitiesConfig",
    "localhub.apps.bookmarks.apps.BookmarksConfig",
    "localhub.apps.comments.apps.CommentsConfig",
    "localhub.apps.communities.apps.CommunitiesConfig",
    "localhub.apps.events.apps.EventsConfig",
    "localhub.apps.flags.apps.FlagsConfig",
    "localhub.apps.hashtags.apps.HashtagsConfig",
    "localhub.apps.invites.apps.InvitesConfig",
    "localhub.apps.join_requests.apps.JoinRequestsConfig",
    "localhub.apps.likes.apps.LikesConfig",
    "localhub.apps.notifications.apps.NotificationsConfig",
    "localhub.apps.photos.apps.PhotosConfig",
    "localhub.apps.polls.apps.PollsConfig",
    "localhub.apps.posts.apps.PostsConfig",
    "localhub.apps.private_messages.apps.PrivateMessagesConfig",
    "localhub.apps.users.apps.UsersConfig",
]


INSTALLED_APPS = [
    # grappelli must go before django-admin
    "grappelli",
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
    "localhub.middleware.turbolinks.TurbolinksMiddleware",
    "localhub.apps.communities.middleware.CurrentCommunityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "localhub.apps.users.middleware.UserLocaleMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "localhub.middleware.http.HttpResponseNotAllowedMiddleware",
]

# base Django admin URL (should be something obscure in production)

ADMIN_URL = env.str("ADMIN_URL", default="admin/")

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

ACCOUNT_USER_DISPLAY = "localhub.apps.users.utils.user_display"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email",],
        "AUTH_PARAMS": {"access_type": "online",},
    }
}

SOCIALACCOUNT_ADAPTER = "localhub.apps.users.adapters.SocialAccountAdapter"

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English (US)"),
    ("en-gb", "English (GB)"),
    ("fi", "Suomi"),
]
LANGUAGE_COOKIE_DOMAIN = env.str("LANGUAGE_COOKIE_DOMAIN", default=None)

LOCALE_PATHS = [str(root.path("i18n"))]

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

MARKDOWNX_MARKDOWNIFY_FUNCTION = "localhub.markdown.utils.markdownify"

MARKDOWNX_MARKDOWN_EXTENSIONS = [
    "pymdownx.extra",
    "pymdownx.emoji",
    "codehilite",
    "localhub.markdown.extensions:NewTabExtension",
    "localhub.markdown.extensions:SafeImageExtension",
]

MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
    "pymdownx.emoji": {
        "emoji_generator": pymdownx.emoji.to_alt,
        "emoji_index": pymdownx.emoji.twemoji,
    }
}

# https://micawber.readthedocs.io/en/latest/django.html
MICAWBER_PROVIDERS = "localhub.apps.activities.oembed.bootstrap_oembed"
MICAWBER_TEMPLATE_EXTENSIONS = [("oembed_no_urlize", {"urlize_all": False})]

# https://celery.readthedocs.io/en/latest/userguide/configuration.html
CELERY_RESULT_BACKEND = CELERY_BROKER_URL = REDIS_URL
CELERY_TASK_SERIALIZER = CELERY_RESULT_SERIALIZER = "json"

# https://django-grappelli.readthedocs.io/en/latest/customization.html

GRAPPELLI_ADMIN_TITLE = env.str("ADMIN_TITLE", default="Localhub Admin")

# https://django-taggit.readthedocs.io/en/latest/getting_started.html

TAGGIT_CASE_INSENSITIVE = True

# https://web-push-codelab.glitch.me/

VAPID_PUBLIC_KEY = env.str("VAPID_PUBLIC_KEY", default=None)
VAPID_PRIVATE_KEY = env.str("VAPID_PRIVATE_KEY", default=None)
VAPID_ADMIN_EMAIL = env.str("VAPID_ADMIN_EMAIL", default=None)

WEBPUSH_ENABLED = env.bool("WEBPUSH_ENABLED", default=True)

GEOLOCATOR_USER_AGENT = env.str("GEOLOCATOR_USER_AGENT", default="localhub.locator")

MEDIA_URL = env.str("MEDIA_URL", default="/media/")
STATIC_URL = env.str("STATIC_URL", default="/static/")

MEDIA_ROOT = str(root.path("media"))
STATIC_ROOT = str(root.path("static"))
STATICFILES_DIRS = [str(root.path("assets"))]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(root.path("templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": False,
            "builtins": [
                "localhub.template.defaultfilters",
                "localhub.template.defaulttags",
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
                "localhub.apps.communities.context_processors.community",
                "localhub.template.context_processors.home_page_url",
            ],
            "libraries": {"pagination": "localhub.pagination.templatetags"},
        },
    }
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"root": {"handlers": ["console"], "level": "INFO"}},
}
