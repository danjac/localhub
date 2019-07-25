# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.models import Community, Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.types import ContextDict
from localhub.invites.emails import send_invitation_email
from localhub.invites.forms import InviteForm
from localhub.invites.models import Invite


class InviteQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Invite.objects.filter(community=self.request.community)


class SingleInviteMixin(InviteQuerySetMixin, SingleObjectMixin):
    ...


class MultipleInviteMixin(InviteQuerySetMixin, MultipleObjectMixin):
    ...


class SingleInviteView(SingleInviteMixin, View):
    ...


class InviteListView(
    LoginRequiredMixin, PermissionRequiredMixin, MultipleInviteMixin, ListView
):
    permission_required = "communities.manage_community"

    def get_permission_object(self) -> Community:
        return self.request.community


invite_list_view = InviteListView.as_view()


class InviteCreateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    model = Invite
    form_class = InviteForm
    success_url = reverse_lazy("invites:list")
    permission_required = "communities.manage_community"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_form_kwargs(self) -> ContextDict:
        kwargs = super().get_form_kwargs()
        kwargs.update({"community": self.request.community})
        return kwargs

    def form_valid(self, form: InviteForm) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.sender = self.request.user
        self.object.community = self.request.community
        self.object.sent = timezone.now()
        self.object.save()

        # send email to recipient
        send_invitation_email(self.object)

        messages.success(
            self.request,
            _("Your invitation has been sent to %s") % self.object.email,
        )

        return HttpResponseRedirect(self.get_success_url())


invite_create_view = InviteCreateView.as_view()


class InviteResendView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleInviteView
):
    permission_required = "communities.manage_community"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=Invite.STATUS.pending)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # should be a POST, but whatever
        self.object = self.get_object()
        self.object.sent = timezone.now()
        self.object.save()

        send_invitation_email(self.object)
        messages.success(
            self.request, _("Email has been re-sent to %s") % self.object.email
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse("invites:list")


invite_resend_view = InviteResendView.as_view()


class InviteDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleInviteMixin, DeleteView
):
    permission_required = "communities.manage_community"
    success_url = reverse_lazy("invites:list")

    def get_permission_object(self) -> Community:
        return self.request.community


invite_delete_view = InviteDeleteView.as_view()


class InviteAcceptView(SingleInviteView):
    """
    Handles an invite accept action.

    If no current user matches the invite email, then redirects
    the user to sign up (on sign up they are redirected back here to complete
    the invite process).

    If user matches then a new membership instance is created for the
    community and the invite is flagged accordingly.
    """
    allow_if_private = True

    def get_queryset(self) -> QuerySet:
        # TBD: add a deadline of e.g. 3 days
        return super().get_queryset().filter(status=Invite.STATUS.pending)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        user = get_user_model().objects.for_email(self.object.email).first()

        if request.user.is_anonymous:
            if user:
                return self.handle_logged_out_user()
            return self.handle_new_user()

        if user == request.user:
            return self.handle_current_user()

        return self.handle_invalid_invite()

    def handle_new_user(self) -> HttpResponse:
        messages.info(self.request, _("Sign up to join this community"))
        return redirect_to_login(
            self.request.get_full_path(), reverse("account_signup")
        )

    def handle_logged_out_user(self) -> HttpResponse:
        messages.info(self.request, _("Login to join this community"))
        return redirect_to_login(self.request.get_full_path())

    def handle_current_user(self) -> HttpResponse:
        _membership, created = Membership.objects.get_or_create(
            member=self.request.user, community=self.object.community
        )

        if created:
            message = _("Welcome to %s") % self.object.community.name
        else:
            message = _("You are already a member of this community")

        messages.success(self.request, message)

        self.object.status = Invite.STATUS.accepted
        self.object.save()

        return HttpResponseRedirect(settings.HOME_PAGE_URL)

    def handle_invalid_invite(self) -> HttpResponse:
        messages.error(self.request, _("This invite is invalid"))

        self.object.status = Invite.STATUS.rejected
        self.object.save()

        return HttpResponseRedirect(settings.HOME_PAGE_URL)


invite_accept_view = InviteAcceptView.as_view()
