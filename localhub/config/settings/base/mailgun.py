# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Local
from . import INSTALLED_APPS, env

CELERY_EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

MAILGUN_API_KEY = env.str("MAILGUN_API_KEY")
MAILGUN_SENDER_DOMAIN = env.str("MAILGUN_SENDER_DOMAIN")

ANYMAIL = {
    "MAILGUN_API_KEY": MAILGUN_API_KEY,
    "MAILGUN_SENDER_DOMAIN": MAILGUN_SENDER_DOMAIN,
}

SERVER_EMAIL = f"errors@{MAILGUN_SENDER_DOMAIN}"
DEFAULT_FROM_EMAIL = f"support@{MAILGUN_SENDER_DOMAIN}"

INSTALLED_APPS += ["anymail"]
