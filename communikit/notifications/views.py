# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin

from communikit.comments.models import CommentNotification
from communikit.communities.views import CommunityRequiredMixin
from communikit.core.types import QuerySetList
from communikit.core.views import CombinedQuerySetListView
from communikit.notifications import app_settings
from communikit.posts.models import PostNotification


class NotificationListView(
    CommunityRequiredMixin, LoginRequiredMixin, CombinedQuerySetListView
):
    paginate_by = app_settings.DEFAULT_PAGE_SIZE
    template_name = "notifications/notification_list.html"

    def get_querysets(self) -> QuerySetList:
        return [
            PostNotification.objects.filter(
                recipient=self.request.user,
                post__community=self.request.community,
            ).select_related("post", "post__owner"),
            CommentNotification.objects.filter(
                recipient=self.request.user,
                comment__activity__community=self.request.community,
            ).select_related("comment", "comment__owner"),
        ]


notification_list_view = NotificationListView.as_view()
