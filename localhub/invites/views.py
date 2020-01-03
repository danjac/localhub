# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import CreateView, DeleteView, GenericModelView, ListView

from localhub.communities.models import Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.users.notifications import send_user_notification

from .emails import send_invitation_email
from .forms import InviteForm
from .models import Invite


class InviteQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Invite.objects.filter(community=self.request.community)


class BaseSingleInviteView(InviteQuerySetMixin, GenericModelView):
    ...


class InviteAdminMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = "communities.manage_community"


class InviteListView(
    InviteAdminMixin, InviteQuerySetMixin, ListView
):
    model = Invite

    def get_permission_object(self):
        return self.request.community


invite_list_view = InviteListView.as_view()


class InviteCreateView(
    InviteAdminMixin, CommunityRequiredMixin, CreateView,
):
    model = Invite
    form_class = InviteForm
    success_url = reverse_lazy("invites:list")

    def get_permission_object(self):
        return self.request.community

    def get_form(self, data=None, files=None):
        return self.form_class(self.request.community, data, files)

    def form_valid(self, form):
        invite = form.save(commit=False)
        invite.sender = self.request.user
        invite.community = self.request.community
        invite.sent = timezone.now()
        invite.save()

        # send email to recipient
        send_invitation_email(invite)

        messages.success(
            self.request, _("Your invitation has been sent to %s") % invite.email,
        )

        return HttpResponseRedirect(self.get_success_url())


invite_create_view = InviteCreateView.as_view()


class InviteResendView(
    InviteAdminMixin, BaseSingleInviteView
):

    def get_permission_object(self):
        return self.request.community

    def get_queryset(self):
        return super().get_queryset().filter(status=Invite.STATUS.pending)

    def get(self, request, *args, **kwargs):
        invite = self.get_object()
        invite.sent = timezone.now()
        invite.save()

        send_invitation_email(invite)
        messages.success(self.request, _("Email has been re-sent to %s") % invite.email)
        return redirect("invites:list")


invite_resend_view = InviteResendView.as_view()


class InviteDeleteView(
    InviteAdminMixin, InviteQuerySetMixin, DeleteView,
):
    success_url = reverse_lazy("invites:list")
    model = Invite

    def get_permission_object(self):
        return self.request.community


invite_delete_view = InviteDeleteView.as_view()


class InviteAcceptView(BaseSingleInviteView):
    """
    Handles an invite accept action.

    If no current user matches the invite email, then redirects
    the user to sign up (on sign up they are redirected back here to complete
    the invite process).

    If user matches then a new membership instance is created for the
    community and the invite is flagged accordingly.
    """

    allow_non_members = True

    def get_queryset(self):
        # TBD: add a deadline of e.g. 3 days
        return super().get_queryset().filter(status=Invite.STATUS.pending)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = get_user_model().objects.for_email(self.object.email).first()

        if request.user.is_anonymous:
            if user:
                return self.handle_logged_out_user()
            return self.handle_new_user()

        if user == request.user:
            return self.handle_current_user()

        return self.handle_invalid_invite()

    def handle_new_user(self):
        messages.info(self.request, _("Sign up to join this community"))
        return redirect_to_login(
            self.request.get_full_path(), reverse("account_signup")
        )

    def handle_logged_out_user(self):
        messages.info(self.request, _("Login to join this community"))
        return redirect_to_login(self.request.get_full_path())

    def handle_current_user(self):
        _membership, created = Membership.objects.get_or_create(
            member=self.request.user, community=self.object.community
        )

        if created:
            message = _("Welcome to %s") % self.object.community.name
            for notification in self.request.user.notify_on_join(self.object.community):
                send_user_notification(self.request.user, notification)
        else:
            message = _("You are already a member of this community")

        messages.success(self.request, message)

        self.object.status = Invite.STATUS.accepted
        self.object.save()

        return HttpResponseRedirect(settings.HOME_PAGE_URL)

    def handle_invalid_invite(self):
        messages.error(self.request, _("This invite is invalid"))

        self.object.status = Invite.STATUS.rejected
        self.object.save()

        return HttpResponseRedirect(settings.HOME_PAGE_URL)


invite_accept_view = InviteAcceptView.as_view()
