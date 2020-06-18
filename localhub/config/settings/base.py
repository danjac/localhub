# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import os
import pathlib
import re

# Django
from django.contrib import messages
from django.urls import reverse_lazy

# Third Party Libraries
import pymdownx.emoji
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
    ALLOWED_HOSTS = []

    SESSION_COOKIE_DOMAIN = values.Value()
    CSRF_COOKIE_DOMAIN = values.Value()
    LANGUAGE_COOKIE_DOMAIN = values.Value()
    CSRF_TRUSTED_ORIGINS = []

    WSGI_APPLICATION = "localhub.config.wsgi.application"

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
        "rules.apps.AutodiscoverRulesConfig",
        "sorl.thumbnail",
        "taggit",
        "widget_tweaks",
    ]

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
    ]

    ROOT_URLCONF = "localhub.config.urls"

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

    MARKDOWNX_MARKDOWNIFY_FUNCTION = "localhub.markdown.utils.markdownify"

    MARKDOWNX_MARKDOWN_EXTENSIONS = [
        "pymdownx.extra",
        "pymdownx.emoji",
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

    # https://django-taggit.readthedocs.io/en/latest/getting_started.html

    TAGGIT_CASE_INSENSITIVE = True

    # https://web-push-codelab.glitch.me/

    LOCALHUB_VAPID_PUBLIC_KEY = values.Value()
    LOCALHUB_VAPID_PRIVATE_KEY = values.Value()
    LOCALHUB_VAPID_ADMIN_EMAIL = values.Value()

    LOCALHUB_WEBPUSH_ENABLED = values.BooleanValue(True)

    LOCALHUB_DEFAULT_PAGE_SIZE = 12
    LOCALHUB_HOME_PAGE_URL = reverse_lazy("activity_stream")
    LOCALHUB_GEOLOCATOR_USER_AGENT = values.Value("localhub.locator")

    LOCALHUB_HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")
    LOCALHUB_HASHTAGS_TYPEAHEAD_CONFIG = (
        "#",
        reverse_lazy("hashtags:autocomplete_list"),
    )

    LOCALHUB_MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>!.?[\]|{}]+)")
    LOCALHUB_MENTIONS_TYPEAHEAD_CONFIG = (
        "@",
        reverse_lazy("users:autocomplete_list"),
    )

    @property
    def BASE_DIR(self):
        return str(pathlib.Path(__file__).parents[3])

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
        return self.LOCALHUB_HOME_PAGE_URL

    @property
    def LOCALHUB_LONG_PAGE_SIZE(self):
        return self.LOCALHUB_DEFAULT_PAGE_SIZE * 2
