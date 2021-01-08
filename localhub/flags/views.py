# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.conf import settings
from django.views.generic import DeleteView, ListView

# Third Party Libraries
from turbo_response import HttpResponseSeeOther
from turbo_response.views import TurboCreateView

# Localhub
from localhub.common.mixins import ParentObjectMixin

# Local
from .forms import FlagForm
from .mixins import FlagQuerySetMixin
from .models import Flag


class BaseFlagCreateView(
    ParentObjectMixin, TurboCreateView,
):
    form_class = FlagForm
    template_name = "flags/flag_form.html"

    def get_success_url(self):
        return self.parent.get_absolute_url()

    def form_valid(self, form):
        flag = form.save(commit=False)
        flag.content_object = self.parent
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()

        flag.notify()

        return HttpResponseSeeOther(self.get_success_url())


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


class FlagDeleteView(FlagQuerySetMixin, DeleteView):
    model = Flag

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()


flag_delete_view = FlagDeleteView.as_view()
