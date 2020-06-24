# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

# Localhub
from localhub.config.app_settings import HOME_PAGE_URL


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        return HOME_PAGE_URL
