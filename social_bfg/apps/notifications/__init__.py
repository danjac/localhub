# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.utils.module_loading import autodiscover_modules


def autodiscover():
    autodiscover_modules("notifications")
