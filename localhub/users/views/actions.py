# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, View

from rules.contrib.views import PermissionRequiredMixin

from localhub.views import SuccessActionView

from .mixins import CurrentUserMixin, UserQuerySetMixin


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()


class BaseUserActionView(UserQuerySetMixin, SuccessActionView):
    slug_field = "username"
    slug_url_kwarg = "username"


class BaseFollowUserView(
    PermissionRequiredMixin, BaseUserActionView,
):
    permission_required = "users.follow_user"
    is_success_ajax_response = True
    exclude_blocking_users = True


class UserFollowView(BaseFollowUserView):
    success_message = _("You are now following %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following.add(self.object)
        self.request.user.notify_on_follow(self.object, self.request.community)

        return self.success_response()


user_follow_view = UserFollowView.as_view()


class UserUnfollowView(BaseFollowUserView):
    success_message = _("You are no longer following %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following.remove(self.object)
        return self.success_response()


user_unfollow_view = UserUnfollowView.as_view()


class BaseUserBlockView(PermissionRequiredMixin, BaseUserActionView):
    permission_required = "users.block_user"


class UserBlockView(BaseUserBlockView):
    success_message = _("You are now blocking %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.block_user(self.object)
        return self.success_response()


user_block_view = UserBlockView.as_view()


class UserUnblockView(BaseUserBlockView):
    success_message = _("You are no longer blocking %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.blocked.remove(self.object)
        return self.success_response()


user_unblock_view = UserUnblockView.as_view()


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()


class DismissNoticeView(CurrentUserMixin, View):
    def post(self, request, notice):
        self.request.user.dismiss_notice(notice)
        return HttpResponse()


dismiss_notice_view = DismissNoticeView.as_view()
