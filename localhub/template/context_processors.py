# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings


def darkmode(request):
    return {"darkmode": "darkmode" in request.COOKIES}


def home_page_url(request):
    return {"home_page_url": settings.LOCALHUB_HOME_PAGE_URL}
