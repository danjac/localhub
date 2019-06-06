# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.cache import cache

from micawber import providers


def bootstrap_noembed():
    return providers.bootstrap_noembed(cache, nowrap=1)
