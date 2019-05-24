# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from communikit.comments.models import CommentNotification
from communikit.communities.views import CommunityRequiredMixin
from communikit.core.views import CombinedQuerySetListView
from communikit.notifications import app_settings
from communikit.posts.models import PostNotification


class NotificationsView(
    CommunityRequiredMixin, LoginRequiredMixin, CombinedQuerySetListView
):
    paginate_by = app_settings.DEFAULT_PAGE_SIZE
    template_name = "notifications/notification_list.html"

    def get_querysets(self) -> List[QuerySet]:
        return [
            PostNotification.objects.filter(
                recipient=self.request.user, community=self.request.community
            ).select_related("owner"),
            CommentNotification.objects.filter(
                recipient=self.request.user,
                activity__community=self.request.community,
            ).select_related("owner", "activity__owner"),
        ]
