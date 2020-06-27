# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Local
from .base import *  # noqa
from .base import env
from .base.aws import *  # noqa
from .base.mailgun import *  # noqa
from .base.secure import *  # noqa

# Required for Heroku SSL
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

BROKER_TRANSPORT_OPTIONS = {
    "max_connections": env.int("MAX_BROKER_CONNECTIONS", default=2),
}
