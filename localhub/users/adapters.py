# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        return settings.HOME_PAGE_URL

    def get_connect_redirect_url(self, request, socialaccount):
        return settings.HOME_PAGE_URL
