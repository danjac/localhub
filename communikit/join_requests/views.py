from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.models import Community, Membership
from communikit.communities.views import CommunityRequiredMixin
from communikit.invites.emails import send_invitation_email
from communikit.invites.models import Invite
from communikit.join_requests.emails import (
    send_acceptance_email,
    send_join_request_email,
    send_rejection_email,
)
from communikit.join_requests.forms import JoinRequestForm
from communikit.join_requests.models import JoinRequest
from communikit.types import ContextDict


class CommunityJoinRequestQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return JoinRequest.objects.filter(community=self.request.community)


class JoinRequestListView(
    LoginRequiredMixin,
    CommunityJoinRequestQuerySetMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_required = "communities.manage_community"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related("community", "sender")


join_request_list_view = JoinRequestListView.as_view()


class JoinRequestCreateView(CommunityRequiredMixin, CreateView):
    model = JoinRequest
    form_class = JoinRequestForm
    success_url = settings.COMMUNIKIT_HOME_PAGE_URL
    allow_if_private = True

    def get_form_kwargs(self) -> ContextDict:
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {"community": self.request.community, "sender": self.request.user}
        )
        return kwargs

    def form_valid(self, form: JoinRequestForm) -> HttpResponse:
        self.object = form.save()
        send_join_request_email(self.object)

        messages.success(
            self.request,
            _("Your request has been sent to the community admins"),
        )

        return HttpResponseRedirect(self.get_success_url())


join_request_create_view = JoinRequestCreateView.as_view()


class JoinRequestActionView(
    CommunityJoinRequestQuerySetMixin,
    PermissionRequiredMixin,
    SingleObjectMixin,
    View,
):

    permission_required = "communities.manage_community"
    success_url = reverse_lazy("join_requests:list")

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=JoinRequest.STATUS.pending)

    def get_success_url(self) -> str:
        return self.success_url


class JoinRequestAcceptView(JoinRequestActionView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # TBD: needs to be ajax POST/confirm page
        self.object = self.get_object()
        self.object.status = JoinRequest.STATUS.accepted
        self.object.save()

        user = self.object.get_sender()

        if user:
            _membership, created = Membership.objects.get_or_create(
                member=user, community=self.object.community
            )
            if created:
                send_acceptance_email(self.object)
                messages.success(request, _("Join request has been accepted"))

            else:
                messages.error(
                    request, _("User already belongs to this community")
                )
        else:
            invite, created = Invite.objects.get_or_create(
                sender=request.user,
                community=self.object.community,
                email=self.object.email,
            )
            if created:
                send_invitation_email(invite)
                messages.success(
                    self.request, _("An invite has been sent to this email")
                )

        return HttpResponseRedirect(self.get_success_url())


join_request_accept_view = JoinRequestAcceptView.as_view()


class JoinRequestRejectView(JoinRequestActionView):
    # TBD: needs to be ajax POST/confirm page
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        self.object.status = JoinRequest.STATUS.rejected
        self.object.save()

        send_rejection_email(self.object)

        messages.info(self.request, _("Join request has been rejected"))

        return HttpResponseRedirect(self.get_success_url())


join_request_reject_view = JoinRequestRejectView.as_view()
