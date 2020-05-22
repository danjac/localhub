# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

# Social-BFG
from social_bfg.apps.communities.serializers import CommunitySerializer
from social_bfg.apps.users.serializers import AuthenticatedUserSerializer


class FrontendView(TemplateView):
    """Hosts the SPA frontend of the application.
    """

    template_name = "frontend.html"

    def get_init_data(self):
        return {
            "user": AuthenticatedUserSerializer(self.request.user).data
            if self.request.user.is_authenticated
            else None,
            "community": CommunitySerializer(self.request.community).data
            if self.request.community.active
            else None,
        }

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update({"init_data": self.get_init_data()})
        return data


frontend_view = never_cache(ensure_csrf_cookie(FrontendView.as_view()))
