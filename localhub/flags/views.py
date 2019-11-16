# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from rules.contrib.views import PermissionRequiredMixin
from vanilla import DeleteView, ListView

from localhub.communities.views import CommunityRequiredMixin

from .models import Flag


class FlagQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Flag.objects.filter(community=self.request.community)


class FlagPermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = "communities.moderate_community"

    def get_permission_object(self):
        return self.request.community


class FlagListView(FlagPermissionRequiredMixin, FlagQuerySetMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE
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


class FlagDeleteView(FlagPermissionRequiredMixin, FlagQuerySetMixin, DeleteView):
    model = Flag

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()


flag_delete_view = FlagDeleteView.as_view()
