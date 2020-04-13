# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import GenericModelView

from localhub.views import SuccessMixin

from .mixins import TagQuerySetMixin


class BaseTagActionView(
    TagQuerySetMixin, PermissionRequiredMixin, SuccessMixin, GenericModelView
):
    ...


class BaseTagFollowView(BaseTagActionView):
    permission_required = "users.follow_tag"
    template_name = "hashtags/includes/follow.html"
    is_success_ajax_response = True

    def get_permission_object(self):
        return self.request.community


class TagFollowView(BaseTagFollowView):
    success_message = _("You are now following #%(object)s")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.following_tags.add(self.object)
        return self.success_response()


tag_follow_view = TagFollowView.as_view()


class TagUnfollowView(BaseTagFollowView):
    success_message = _("You are no longer following #%(object)s")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.following_tags.remove(self.object)
        return self.success_response()


tag_unfollow_view = TagUnfollowView.as_view()


class BaseTagBlockView(BaseTagActionView):
    permission_required = "users.block_tag"
    is_success_ajax_response = True

    def get_permission_object(self):
        return self.request.community


class TagBlockView(BaseTagBlockView):
    success_message = _("You are now blocking #%(object)s")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked_tags.add(self.object)
        return self.success_response()


tag_block_view = TagBlockView.as_view()


class TagUnblockView(BaseTagBlockView):
    success_message = _("You are no longer blocking #%(object)s")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked_tags.remove(self.object)
        return self.success_response()


tag_unblock_view = TagUnblockView.as_view()
