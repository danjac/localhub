# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from vanilla import ListView

from localhub.communities.views import (
    CommunityModeratorRequiredMixin,
    CommunityRequiredMixin,
)
from localhub.views import SuccessDeleteView

from .models import Flag


class FlagQuerySetMixin(CommunityRequiredMixin, CommunityModeratorRequiredMixin):
    def get_queryset(self):
        return Flag.objects.filter(community=self.request.community)


class FlagListView(FlagQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE
    model = Flag

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user", "content_type")
            .prefetch_related("content_object")
            .order_by("-created")
        )


flag_list_view = FlagListView.as_view()


class FlagDeleteView(FlagQuerySetMixin, SuccessDeleteView):
    model = Flag


flag_delete_view = FlagDeleteView.as_view()
