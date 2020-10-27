# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Localhub
from localhub.communities.mixins import CommunityRequiredMixin


class ActivityQuerySetMixin(CommunityRequiredMixin):
    model = None

    def get_queryset(self):
        return self.model._default_manager.for_community(
            self.request.community
        ).select_related("owner", "community", "parent", "parent__owner")


class ActivityTemplateMixin:
    """Includes extra template name option of "activities/activity_{suffix}.html" """

    def get_template_names(self):
        return super().get_template_names() + [
            f"activities/activity{self.template_name_suffix}.html"
        ]
