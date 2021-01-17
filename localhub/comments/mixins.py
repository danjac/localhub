# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Localhub
from localhub.communities.mixins import CommunityRequiredMixin

# Local
from .models import Comment


class CommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Comment.objects.for_community(self.request.community).select_related(
            "owner",
            "community",
            "parent",
            "parent__owner",
            "parent__community",
        )
