# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Localhub
from localhub.config.app_settings import HOME_PAGE_URL


def home_page_url(request):
    return {"home_page_url": HOME_PAGE_URL}
