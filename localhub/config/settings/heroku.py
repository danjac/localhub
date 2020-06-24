# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Local
from .aws import *  # noqa
from .base import *  # noqa
from .mailgun import *  # noqa
from .secure import *  # noqa

# Required for Heroku SSL
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
