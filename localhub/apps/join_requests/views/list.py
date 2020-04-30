# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, IntegerField, Value, When
from django.utils.functional import cached_property
from django.views.generic import ListView

from localhub.common.views import SearchMixin

from ..models import JoinRequest
from .mixins import JoinRequestAdminMixin, JoinRequestQuerySetMixin


class JoinRequestListView(
    JoinRequestQuerySetMixin, JoinRequestAdminMixin, SearchMixin, ListView
):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE
    model = JoinRequest

    @cached_property
    def status(self):
        status = self.request.GET.get("status")
        if status in JoinRequest.Status.values and self.total_count:
            return status
        return None

    @cached_property
    def status_display(self):
        return dict(JoinRequest.Status.choices)[self.status] if self.status else None

    @cached_property
    def total_count(self):
        return super().get_queryset().count()

    def get_queryset(self):
        qs = super().get_queryset().select_related("community", "sender")
        if self.search_query:
            qs = qs.search(self.search_query)

        if self.status:
            qs = qs.filter(status=self.status).order_by("-created")
        else:
            qs = qs.annotate(
                priority=Case(
                    When(status=JoinRequest.Status.PENDING, then=Value(1)),
                    default_value=0,
                    output_field=IntegerField(),
                )
            ).order_by("priority", "-created")
        return qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "total_count": self.total_count,
                "status": self.status,
                "status_display": self.status_display,
                "status_choices": list(JoinRequest.Status.choices),
            }
        )
        return data


join_request_list_view = JoinRequestListView.as_view()


class SentJoinRequestListView(LoginRequiredMixin, ListView):
    """
    List of pending join requests sent by this user
    """

    model = JoinRequest
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE
    template_name = "join_requests/sent_joinrequest_list.html"

    def get_queryset(self):
        return (
            JoinRequest.objects.pending()
            .for_sender(self.request.user)
            .select_related("community")
            .order_by("-created")
        )


sent_join_request_list_view = SentJoinRequestListView.as_view()
