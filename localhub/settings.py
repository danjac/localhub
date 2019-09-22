# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import socket


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
    ALLOWED_HOSTS = []

    SESSION_COOKIE_DOMAIN = values.Value()
    CSRF_COOKIE_DOMAIN = values.Value()
    LANGUAGE_COOKIE_DOMAIN = values.Value()
    CSRF_TRUSTED_ORIGINS = []

    WSGI_APPLICATION = "localhub.wsgi.application"

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
        "channels",
        "djcelery_email",
        "markdownx",
        "micawber.contrib.mcdjango",
        "rules.apps.AutodiscoverRulesConfig",
        "simple_history",
        "sorl.thumbnail",
        "taggit",
        "widget_tweaks",
    ]

    LOCAL_APPS = [
        "localhub.activities.apps.ActivitiesConfig",
        "localhub.comments.apps.CommentsConfig",
        "localhub.communities.apps.CommunitiesConfig",
        "localhub.events.apps.EventsConfig",
        "localhub.flags.apps.FlagsConfig",
        "localhub.invites.apps.InvitesConfig",
        "localhub.join_requests.apps.JoinRequestsConfig",
        "localhub.likes.apps.LikesConfig",
        "localhub.notifications.apps.NotificationsConfig",
        "localhub.photos.apps.PhotosConfig",
        "localhub.polls.apps.PollsConfig",
        "localhub.posts.apps.PostsConfig",
        "localhub.private_messages.apps.PrivateMessagesConfig",
        "localhub.users.apps.UsersConfig",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sites.middleware.CurrentSiteMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "localhub.common.middleware.TurbolinksMiddleware",
        "localhub.common.middleware.DoNotTrackMiddleware",
        "localhub.communities.middleware.CurrentCommunityMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.middleware.gzip.GZipMiddleware",
        "localhub.users.middleware.UserLocaleMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "localhub.urls"

    # project-specific

    DEFAULT_PAGE_SIZE = 12

    HOME_PAGE_URL = reverse_lazy("activities:stream")

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

    ACCOUNT_USER_DISPLAY = "localhub.users.utils.user_display"
    ACCOUNT_EMAIL_REQUIRED = True

    # Internationalization
    # https://docs.djangoproject.com/en/2.2/topics/i18n/

    LANGUAGE_CODE = "en"
    LANGUAGES = [("en", "English"), ("fi", "Suomi")]

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # https://docs.djangoproject.com/en/1.11/ref/forms/renderers/

    FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

    # https://neutronx.github.io/django-markdownx/customization/

    MARKDOWNX_MARKDOWNIFY_FUNCTION = (
        "localhub.common.markdown.utils.markdownify"
    )

    # https://micawber.readthedocs.io/en/latest/django.html
    MICAWBER_PROVIDERS = "localhub.activities.oembed.bootstrap_oembed"
    MICAWBER_TEMPLATE_EXTENSIONS = [
        ("oembed_no_urlize", {"urlize_all": False})
    ]
    # https://celery.readthedocs.io/en/latest/userguide/configuration.html

    CELERY_RESULT_BACKEND = CELERY_BROKER_URL = REDIS_URL
    CELERY_TASK_SERIALIZER = CELERY_RESULT_SERIALIZER = "json"

    # https://django-taggit.readthedocs.io/en/latest/getting_started.html

    TAGGIT_CASE_INSENSITIVE = True

    # https://web-push-codelab.glitch.me/
    VAPID_PUBLIC_KEY = values.Value()
    VAPID_PRIVATE_KEY = values.Value()
    VAPID_ADMIN_EMAIL = values.Value()

    # Django channels

    ASGI_APPLICATION = "localhub.routing.application"

    @property
    def CHANNEL_LAYERS(self):
        return {
            "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {"hosts": [self.REDIS_URL]},
            }
        }

    @property
    def BASE_DIR(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
                    ],
                    "libraries": {
                        "form_tags": "localhub.common.forms.templatetags",
                        "pagination_tags": "localhub.common.pagination.templatetags",  # noqa
                    },
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
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient"
                },
            }
        }

    @property
    def LOCALE_PATHS(self):
        return [os.path.join(self.BASE_DIR, "locale")]


class DockerConfigMixin:
    @property
    def INTERNAL_IPS(self):
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
    THIRD_PARTY_APPS = Base.THIRD_PARTY_APPS + ["django_extensions"]
    SITE_ID = 1

    VAPID_PUBLIC_KEY = None
    VAPID_PRIVATE_KEY = None
    VAPID_ADMIN_EMAIL = None

    THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.cached_db_kvstore.KVStore"


class Local(DockerConfigMixin, Base):

    DEBUG = True

    ALLOWED_HOSTS = ["*"]

    THIRD_PARTY_APPS = Base.THIRD_PARTY_APPS + [
        "debug_toolbar",
        "django_extensions",
        "silk",
    ]

    MIDDLEWARE = Base.MIDDLEWARE + [
        "silk.middleware.SilkyMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
        "SHOW_TEMPLATE_CONTEXT": True,
    }

    SILKY_PYTHON_PROFILER = True

    SITE_ID = 1


class Production(DockerConfigMixin, Base):

    THIRD_PARTY_APPS = Base.THIRD_PARTY_APPS + ["anymail", "silk"]

    ALLOWED_HOSTS = values.ListValue()
    CSRF_TRUSTED_ORIGINS = values.ListValue()

    ADMINS = values.ListValue()

    SECURE_SSL_REDIRECT = True
    # This is required for Heroku SSL.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    DEFAULT_FILE_STORAGE = "localhub.common.storages.MediaStorage"
    STATICFILES_STORAGE = "localhub.common.storages.StaticStorage"

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

    CELERY_EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    MAILGUN_API_KEY = values.Value()
    MAILGUN_SENDER_DOMAIN = values.Value()

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {"django": {"handlers": ["console"], "level": "INFO"}},
    }

    MIDDLEWARE = Base.MIDDLEWARE + ["silk.middleware.SilkyMiddleware"]

    # https://github.com/jazzband/django-silk#configuration

    SILKY_AUTHENTICATION = True  # User must login
    SILKY_AUTHORISATION = True
    SILKY_INTERCEPT_PERCENT = 50
    SILKY_MAX_REQUEST_BODY_SIZE = -1  # Silk takes anything <0 as no limit
    SILKY_MAX_RESPONSE_BODY_SIZE = 1024
    SILKY_MAX_RECORDED_REQUESTS = 10 ** 4

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
