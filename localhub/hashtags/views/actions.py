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

    def get_permission_object(self):
        return self.request.community

    def success_response(self, is_following):
        return self.render_success_to_response(
            {"is_following": is_following, "tag": self.object}
        )


class TagFollowView(BaseTagFollowView):
    success_message = _("You are now following this tag")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.following_tags.add(self.object)
        return self.success_response(is_following=True)


tag_follow_view = TagFollowView.as_view()


class TagUnfollowView(BaseTagFollowView):
    success_message = _("You are no longer following this tag")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.following_tags.remove(self.object)
        return self.success_response(is_following=False)


tag_unfollow_view = TagUnfollowView.as_view()


class BaseTagBlockView(BaseTagActionView):
    permission_required = "users.block_tag"
    template_name = "hashtags/includes/block.html"

    def get_permission_object(self):
        return self.request.community

    def success_response(self, is_blocked):
        return self.render_success_to_response(
            {"tag": self.object, "is_blocked": is_blocked}
        )


class TagBlockView(BaseTagBlockView):
    success_message = _("You are now blocking this tag")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked_tags.add(self.object)
        return self.success_response(is_blocked=True)


tag_block_view = TagBlockView.as_view()


class TagUnblockView(BaseTagBlockView):
    success_message = _("You no longer blocking this tag")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked_tags.remove(self.object)
        return self.success_response(is_blocked=False)


tag_unblock_view = TagUnblockView.as_view()
