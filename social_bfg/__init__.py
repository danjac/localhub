# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Local
from .celery_app import app as celery_app

__all__ = ("celery_app",)
