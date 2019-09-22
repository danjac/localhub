# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

from configurations import importer

from channels.routing import get_default_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "localhub.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

importer.install()

application = get_default_application()
