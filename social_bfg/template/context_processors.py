# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings


def home_page_url(request):
    return {"home_page_url": settings.SOCIAL_BFG_HOME_PAGE_URL}
