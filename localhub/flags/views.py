# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.conf import settings
from django.views.generic import ListView

# Localhub
from localhub.communities.views import (
    CommunityModeratorRequiredMixin,
    CommunityRequiredMixin,
)
from localhub.views import ParentObjectMixin, SuccessCreateView, SuccessDeleteView

# Local
from .forms import FlagForm
from .models import Flag


class FlagQuerySetMixin(CommunityRequiredMixin, CommunityModeratorRequiredMixin):
    def get_queryset(self):
        return Flag.objects.filter(community=self.request.community)


class BaseFlagCreateView(
    ParentObjectMixin, SuccessCreateView,
):
    form_class = FlagForm
    template_name = "flags/flag_form.html"

    def get_success_url(self):
        return super().get_success_url(object=self.parent)

    def form_valid(self, form):
        flag = form.save(commit=False)
        flag.content_object = self.parent
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()

        flag.notify()

        return self.success_response()


class FlagListView(FlagQuerySetMixin, ListView):
    paginate_by = settings.LONG_PAGE_SIZE
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

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()


flag_delete_view = FlagDeleteView.as_view()
