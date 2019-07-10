# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import DeleteView, ListView

from rules.contrib.views import PermissionRequiredMixin

from localite.communities.models import Community
from localite.communities.views import CommunityRequiredMixin
from localite.flags.models import Flag


class FlagQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Flag.objects.filter(community=self.request.community)


class FlagPermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = "communities.moderate_community"

    def get_permission_object(self) -> Community:
        return self.request.community


class FlagListView(FlagPermissionRequiredMixin, FlagQuerySetMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .select_related("user", "content_type")
            .prefetch_related("content_object")
            .order_by("-created")
        )


flag_list_view = FlagListView.as_view()


class FlagDeleteView(
    FlagPermissionRequiredMixin, FlagQuerySetMixin, DeleteView
):
    def get_success_url(self) -> str:
        return self.object.content_object.get_absolute_url()


flag_delete_view = FlagDeleteView.as_view()
