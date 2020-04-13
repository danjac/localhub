# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from rules.contrib.views import PermissionRequiredMixin
from vanilla import GenericModelView

from localhub.views import SuccessMixin

from .mixins import CurrentUserMixin, UserQuerySetMixin


class BaseUserActionView(UserQuerySetMixin, SuccessMixin, GenericModelView):
    lookup_field = "username"
    lookup_url_kwarg = "username"


class BaseFollowUserView(PermissionRequiredMixin, BaseUserActionView):
    permission_required = "users.follow_user"
    is_success_ajax_response = True


class UserFollowView(BaseFollowUserView):
    success_message = _("You are now following %(object)s")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.request.user.following.add(self.object)
        self.request.user.notify_on_follow(self.object, self.request.community)

        return self.success_response()


user_follow_view = UserFollowView.as_view()


class UserUnfollowView(BaseFollowUserView):
    success_message = _("You are no longer following %(object)s")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.following.remove(self.object)
        return self.success_response()


user_unfollow_view = UserUnfollowView.as_view()


class UserBlockView(PermissionRequiredMixin, BaseUserActionView):
    permission_required = "users.block_user"
    success_message = _("You are now blocking %(object)s")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked.add(self.object)
        return self.success_response()


user_block_view = UserBlockView.as_view()


class UserUnblockView(BaseUserActionView):
    success_message = _("You are no longer blocking %(object)s")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked.remove(self.object)
        return self.success_response()


user_unblock_view = UserUnblockView.as_view()


class DismissNoticeView(CurrentUserMixin, View):
    def post(self, request, notice):
        self.request.user.dismiss_notice(notice)
        return HttpResponse()


dismiss_notice_view = DismissNoticeView.as_view()


class SwitchThemeView(View):
    def post(self, request, theme):
        if theme not in settings.LOCALHUB_INSTALLED_THEMES:
            raise Http404()

        response = HttpResponse()
        response.set_cookie(
            "theme",
            theme,
            expires=datetime.datetime.now() + datetime.timedelta(days=365),
            domain=settings.SESSION_COOKIE_DOMAIN,
            httponly=True,
        )
        return response


switch_theme_view = SwitchThemeView.as_view()
