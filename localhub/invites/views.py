# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import DetailView, ListView

# Localhub
from localhub.common.mixins import SearchMixin
from localhub.common.views import (
    SuccessActionView,
    SuccessCreateView,
    SuccessDeleteView,
)
from localhub.communities.mixins import (
    CommunityAdminRequiredMixin,
    CommunityRequiredMixin,
)

# Local
from .emails import send_invitation_email
from .forms import InviteForm
from .mixins import InviteQuerySetMixin, InviteRecipientQuerySetMixin
from .models import Invite


class BaseInviteAdminActionView(
    CommunityAdminRequiredMixin, InviteQuerySetMixin, SuccessActionView
):
    ...


class BaseInviteRecipientActionView(InviteRecipientQuerySetMixin, SuccessActionView):
    ...


class InviteResendView(BaseInviteAdminActionView):
    success_url = reverse_lazy("invites:list")

    def get_queryset(self):
        return super().get_queryset().pending()

    def get_success_message(self):
        return _("Your invitation has been re-sent to %(email)s") % {
            "email": self.object.email
        }

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.sent = timezone.now()
        self.object.save()

        send_invitation_email(self.object)
        return self.success_response()


invite_resend_view = InviteResendView.as_view()


class InviteAcceptView(BaseInviteRecipientActionView):
    """
    Handles an invite accept action.

    If user matches then a new membership instance is created for the
    community and the invite is flagged accordingly.
    """

    def get_success_url(self):
        if (
            self.object.is_accepted()
            and self.request.community == self.object.community
        ):
            return settings.HOME_PAGE_URL
        return reverse("invites:received_list")

    def get_success_message(self):
        return _("You are now a member of %(community)s") % {
            "community": self.object.community.name
        }

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        self.object.accept(self.request.user)
        request.user.notify_on_join(self.object.community)

        return self.success_response()


invite_accept_view = InviteAcceptView.as_view()


class InviteRejectView(BaseInviteRecipientActionView):
    def get_success_url(self):
        if Invite.objects.pending().for_user(self.request.user).exists():
            return reverse("invites:received_list")
        return settings.HOME_PAGE_URL

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.reject()
        return self.success_response()


invite_reject_view = InviteRejectView.as_view()


class InviteCreateView(
    CommunityAdminRequiredMixin, CommunityRequiredMixin, SuccessCreateView,
):
    model = Invite
    form_class = InviteForm
    success_url = reverse_lazy("invites:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"community": self.request.community})
        return kwargs

    def get_success_message(self):
        return _("Your invitation has been sent to %(email)s") % {
            "email": self.object.email
        }

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.sender = self.request.user
        self.object.community = self.request.community
        self.object.sent = timezone.now()
        self.object.save()

        # send email to recipient
        send_invitation_email(self.object)
        return self.success_response()


invite_create_view = InviteCreateView.as_view()


class InviteDeleteView(
    CommunityAdminRequiredMixin, InviteQuerySetMixin, SuccessDeleteView,
):
    success_url = reverse_lazy("invites:list")
    success_message = _("You have deleted this invite")
    model = Invite


invite_delete_view = InviteDeleteView.as_view()


class InviteDetailView(InviteRecipientQuerySetMixin, DetailView):
    ...


invite_detail_view = InviteDetailView.as_view()


class InviteListView(
    CommunityAdminRequiredMixin, InviteQuerySetMixin, SearchMixin, ListView
):
    """
    TBD: list of received pending community invitations
    + counter template tag
    """

    model = Invite
    paginate_by = settings.LONG_PAGE_SIZE

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            qs = qs.filter(email__icontains=self.search_query)

        if self.status:
            qs = qs.filter(status=self.status)

        return qs.order_by("-created")

    @cached_property
    def status(self):
        status = self.request.GET.get("status")
        if status in Invite.Status.values and self.total_count:
            return status
        return None

    @cached_property
    def status_display(self):
        return dict(Invite.Status.choices)[self.status] if self.status else None

    @cached_property
    def total_count(self):
        return super().get_queryset().count()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "total_count": self.total_count,
                "status": self.status,
                "status_display": self.status_display,
                "status_choices": list(Invite.Status.choices),
            }
        )
        return data


invite_list_view = InviteListView.as_view()


class ReceivedInviteListView(InviteRecipientQuerySetMixin, ListView):
    """
    List of pending invites sent to this user from different communities.
    """

    template_name = "invites/received_invite_list.html"
    paginate_by = settings.LONG_PAGE_SIZE

    def get_queryset(self):
        return super().get_queryset().order_by("-created")


received_invite_list_view = ReceivedInviteListView.as_view()
