# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings


def home_page_url(request):
    return {"home_page_url": settings.HOME_PAGE_URL}


def is_cookies_accepted(request):
    return {"accept_cookies": "accept-cookies" in request.COOKIES}


def search(request):
    """Requires localhub.common.middleware.search.SearchMiddleware"""
    return {"search": getattr(request, "search", None)}
