# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import os
import pathlib
import re
import socket

# Django
from django.contrib import messages
from django.urls import reverse_lazy

# Third Party Libraries
import pymdownx.emoji
from configurations import Configuration, values


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
    AWS_DEFAULT_ACL = "public-read"

    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=600"}


class Base(Configuration):

    SECRET_KEY = values.SecretValue()
    DATABASES = values.DatabaseURLValue()
    REDIS_URL = values.Value(environ_name="REDIS_URL", environ_prefix=None)

    ATOMIC_REQUESTS = True

    EMAIL_HOST = values.Value()
    EMAIL_PORT = values.PositiveIntegerValue()

    EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"

    DEBUG = False
    ALLOWED_HOSTS = []

    SESSION_COOKIE_DOMAIN = values.Value()
    CSRF_COOKIE_DOMAIN = values.Value()
    LANGUAGE_COOKIE_DOMAIN = values.Value()
    CSRF_TRUSTED_ORIGINS = []

    WSGI_APPLICATION = "social_bfg.config.wsgi.application"

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
        "allauth.socialaccount.providers.google",
        "django_extensions",
        "djcelery_email",
        "markdownx",
        "micawber.contrib.mcdjango",
        "rest_framework",
        "rules.apps.AutodiscoverRulesConfig",
        "sorl.thumbnail",
        "taggit",
        "widget_tweaks",
    ]

    LOCAL_APPS = [
        "social_bfg.apps.activities.apps.ActivitiesConfig",
        "social_bfg.apps.bookmarks.apps.BookmarksConfig",
        "social_bfg.apps.comments.apps.CommentsConfig",
        "social_bfg.apps.communities.apps.CommunitiesConfig",
        "social_bfg.apps.events.apps.EventsConfig",
        "social_bfg.apps.flags.apps.FlagsConfig",
        "social_bfg.apps.hashtags.apps.HashtagsConfig",
        "social_bfg.apps.invites.apps.InvitesConfig",
        "social_bfg.apps.join_requests.apps.JoinRequestsConfig",
        "social_bfg.apps.likes.apps.LikesConfig",
        "social_bfg.apps.notifications.apps.NotificationsConfig",
        "social_bfg.apps.photos.apps.PhotosConfig",
        "social_bfg.apps.polls.apps.PollsConfig",
        "social_bfg.apps.posts.apps.PostsConfig",
        "social_bfg.apps.private_messages.apps.PrivateMessagesConfig",
        "social_bfg.apps.users.apps.UsersConfig",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sites.middleware.CurrentSiteMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "social_bfg.middleware.turbolinks.TurbolinksMiddleware",
        "social_bfg.apps.communities.middleware.CurrentCommunityMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "social_bfg.apps.users.middleware.UserLocaleMiddleware",
        "django.middleware.gzip.GZipMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "social_bfg.config.urls"

    # base Django admin URL (should be something obscure in production)

    ADMIN_URL = values.Value("admin/")

    # sorl

    THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.redis_kvstore.KVStore"
    THUMBNAIL_REDIS_URL = REDIS_URL

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

    ACCOUNT_USER_DISPLAY = "social_bfg.apps.users.utils.user_display"
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_AUTHENTICATION_METHOD = "username_email"

    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "SCOPE": ["profile", "email",],
            "AUTH_PARAMS": {"access_type": "online",},
        }
    }

    SOCIALACCOUNT_ADAPTER = "social_bfg.apps.users.adapters.SocialAccountAdapter"

    # Internationalization
    # https://docs.djangoproject.com/en/2.2/topics/i18n/

    LANGUAGE_CODE = "en"
    LANGUAGES = [("en", "English (US)"), ("en-gb", "English (GB)"), ("fi", "Suomi")]

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

    MARKDOWNX_MARKDOWNIFY_FUNCTION = "social_bfg.markdown.utils.markdownify"

    MARKDOWNX_MARKDOWN_EXTENSIONS = [
        "pymdownx.extra",
        "pymdownx.emoji",
        "social_bfg.markdown.extensions:NewTabExtension",
        "social_bfg.markdown.extensions:SafeImageExtension",
    ]

    MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
        "pymdownx.emoji": {
            "emoji_generator": pymdownx.emoji.to_alt,
            "emoji_index": pymdownx.emoji.twemoji,
        }
    }

    # https://micawber.readthedocs.io/en/latest/django.html
    MICAWBER_PROVIDERS = "social_bfg.apps.activities.oembed.bootstrap_oembed"
    MICAWBER_TEMPLATE_EXTENSIONS = [("oembed_no_urlize", {"urlize_all": False})]

    # https://celery.readthedocs.io/en/latest/userguide/configuration.html
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL = REDIS_URL
    CELERY_TASK_SERIALIZER = CELERY_RESULT_SERIALIZER = "json"

    # https://django-taggit.readthedocs.io/en/latest/getting_started.html

    TAGGIT_CASE_INSENSITIVE = True

    # https://web-push-codelab.glitch.me/

    SOCIAL_BFG_VAPID_PUBLIC_KEY = values.Value()
    SOCIAL_BFG_VAPID_PRIVATE_KEY = values.Value()
    SOCIAL_BFG_VAPID_ADMIN_EMAIL = values.Value()

    SOCIAL_BFG_WEBPUSH_ENABLED = values.BooleanValue(True)

    SOCIAL_BFG_DEFAULT_PAGE_SIZE = 12
    SOCIAL_BFG_HOME_PAGE_URL = reverse_lazy("activity_stream")
    SOCIAL_BFG_GEOLOCATOR_USER_AGENT = values.Value("social_bfg.locator")

    SOCIAL_BFG_HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")
    SOCIAL_BFG_HASHTAGS_TYPEAHEAD_CONFIG = (
        "#",
        reverse_lazy("hashtags:autocomplete_list"),
    )

    SOCIAL_BFG_MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>!.?[\]|{}]+)")
    SOCIAL_BFG_MENTIONS_TYPEAHEAD_CONFIG = (
        "@",
        reverse_lazy("users:autocomplete_list"),
    )

    @property
    def BASE_DIR(self):
        return str(pathlib.Path(__file__).parents[2])

    @property
    def INSTALLED_APPS(self):
        return self.DJANGO_APPS + self.THIRD_PARTY_APPS + self.LOCAL_APPS

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.2/howto/static-files/

    @property
    def MEDIA_URL(self):
        return "/media/"

    @property
    def STATIC_URL(self):
        return "/static/"

    @property
    def MEDIA_ROOT(self):
        return os.path.join(self.BASE_DIR, "media")

    @property
    def STATIC_ROOT(self):
        return os.path.join(self.BASE_DIR, "static")

    @property
    def STATICFILES_DIRS(self):
        return [os.path.join(self.BASE_DIR, "assets")]

    @property
    def TEMPLATES(self):
        return [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [os.path.join(self.BASE_DIR, "templates")],
                "APP_DIRS": True,
                "OPTIONS": {
                    "debug": self.DEBUG,
                    "builtins": [
                        "social_bfg.template.defaultfilters",
                        "social_bfg.template.defaulttags",
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
                        "social_bfg.apps.communities.context_processors.community",
                        "social_bfg.template.context_processors.home_page_url",
                    ],
                    "libraries": {"pagination": "social_bfg.pagination.templatetags"},
                },
            }
        ]

    # Sorl-thumbnail

    @property
    def THUMBNAIL_DEBUG(self):
        return self.DEBUG

    @property
    def CACHES(self):
        return {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": self.REDIS_URL,
                "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            }
        }

    @property
    def LOCALE_PATHS(self):
        return [os.path.join(self.BASE_DIR, "locale")]

    @property
    def LOGIN_REDIRECT_URL(self):
        return self.SOCIAL_BFG_HOME_PAGE_URL

    @property
    def SOCIAL_BFG_LONG_PAGE_SIZE(self):
        return self.SOCIAL_BFG_DEFAULT_PAGE_SIZE * 2


class Testing(Base):
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    ALLOWED_HOSTS = Configuration.ALLOWED_HOSTS + [".example.com"]
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
    SITE_ID = 1

    THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.cached_db_kvstore.KVStore"


class Local(DockerMixin, Base):

    DEBUG = True

    ALLOWED_HOSTS = ["*"]

    THIRD_PARTY_APPS = Base.THIRD_PARTY_APPS + [
        "debug_toolbar",
    ]

    MIDDLEWARE = Base.MIDDLEWARE + [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
        "SHOW_TEMPLATE_CONTEXT": True,
    }

    SITE_ID = 1


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
        "social_bfg.middleware.http.HttpResponseNotAllowedMiddleware",
    ]


class Deployment(AWSMixin, Production):
    """Settings for running tasks in the deployment pipeline."""


class Heroku(DockerMixin, AWSMixin, MailgunMixin, Production):
    """
    Production settings specific to Heroku docker-based setup.

    See heroku.yml for additional settings.
    """

    # This is required for Heroku SSL.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Stream logging to stdout: use `heroku log` to view
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {"root": {"handlers": ["console"], "level": "INFO"}},
    }
