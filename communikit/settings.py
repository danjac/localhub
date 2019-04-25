import os
import socket

from typing import Sequence, Dict

from configurations import Configuration, values


class Base(Configuration):

    SECRET_KEY = values.SecretValue()
    DATABASES = values.DatabaseURLValue()

    EMAIL_HOST = values.Value()
    EMAIL_PORT = values.PositiveIntegerValue()

    DEBUG = False
    ALLOWED_HOSTS = []

    WSGI_APPLICATION = "communikit.wsgi.application"

    DJANGO_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]

    THIRD_PARTY_APPS = [
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        "widget_tweaks",
        "rules.apps.AutodiscoverRulesConfig",
    ]

    LOCAL_APPS = [
        "communikit.users.apps.UsersAppConfig",
        "communikit.communities.apps.CommunitiesAppConfig",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "communikit.communities.middleware.CurrentCommunityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "communikit.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ]
            },
        }
    ]

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

    LOGIN_REDIRECT_URL = "users:detail"
    LOGIN_URL = "account_login"

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

    @property
    def BASE_DIR(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def INSTALLED_APPS(self) -> Sequence[str]:
        return self.DJANGO_APPS + self.THIRD_PARTY_APPS + self.LOCAL_APPS

    @property
    def STATIC_ROOT(self) -> str:
        return os.path.join(self.BASE_DIR, "static")

    @property
    def STATICFILES_DIRS(self) -> Sequence[str]:
        return [os.path.join(self.BASE_DIR, "assets")]

    @property
    def TEMPLATES(self) -> Sequence[Dict]:
        loaders = [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ]
        if not self.DEBUG:
            loaders = [("django.template.loaders.cached.Loader", loaders)]
        return [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [os.path.join(self.BASE_DIR, "templates")],
                "OPTIONS": {
                    "debug": self.DEBUG,
                    "loaders": loaders,
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


class Testing(Base):
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    ALLOWED_HOSTS = Configuration.ALLOWED_HOSTS + [".example.com"]


class Local(Base):
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

    @property
    def INTERNAL_IPS(self) -> Sequence[str]:
        # Docker configuration
        ips = ["127.0.0.1", "10.0.2.2"]
        _, _, ips = socket.gethostbyname_ex(socket.gethostname())
        ips += [ip[:-1] + "1" for ip in ips]
        return ips
