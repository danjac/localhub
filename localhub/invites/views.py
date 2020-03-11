# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import CreateView, DeleteView, DetailView, GenericModelView, ListView

from localhub.communities.models import Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.users.notifications import send_user_notification
from localhub.views import BreadcrumbsMixin, SearchMixin

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


class InviteListView(InviteAdminMixin, InviteQuerySetMixin, SearchMixin, ListView):
    model = Invite
    paginate_by = settings.DEFAULT_PAGE_SIZE * 2

    def get_permission_object(self):
        return self.request.community

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
        if status in Invite.STATUS and self.total_count:
            return status
        return None

    @cached_property
    def status_display(self):
        return Invite.STATUS[self.status] if self.status else None

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
                "status_choices": list(Invite.STATUS),
            }
        )
        return data


invite_list_view = InviteListView.as_view()


class InviteCreateView(
    InviteAdminMixin, CommunityRequiredMixin, BreadcrumbsMixin, CreateView
):
    model = Invite
    form_class = InviteForm
    success_url = reverse_lazy("invites:list")

    def get_permission_object(self):
        return self.request.community

    def get_breadcrumbs(self):
        return [(reverse("invites:list"), _("Invites")), (None, _("Send invite"))]

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

        return redirect(self.get_success_url())


invite_create_view = InviteCreateView.as_view()


class InviteResendView(InviteAdminMixin, BaseSingleInviteView):
    def get_permission_object(self):
        return self.request.community

    def get_queryset(self):
        return super().get_queryset().pending()

    def post(self, request, *args, **kwargs):
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


class InviteAcceptView(InviteQuerySetMixin, DetailView):
    """
    Handles an invite accept action.

    If user matches then a new membership instance is created for the
    community and the invite is flagged accordingly.
    """

    allow_non_members = True
    template_name = "invites/accept.html"

    def get_queryset(self):
        return super().get_queryset().pending().for_user(self.request.user)

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()
        response = self.validate_invite()
        if response:
            return response

        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        response = self.validate_invite()
        if response:
            return response

        if "reject" in request.POST:
            self.reject_invite()
            messages.info(request, _("Your invitation has been rejected"))
            return redirect(self.get_redirect_url())

        try:
            Membership.objects.create(
                member=request.user, community=self.object.community
            )
            messages.success(
                request,
                _("Welcome to %(community)s")
                % {"community": self.object.community.name},
            )
            for notification in request.user.notify_on_join(self.object.community):
                send_user_notification(request.user, notification)
        except IntegrityError:
            pass

        self.accept_invite()

        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        return settings.HOME_PAGE_URL

    def save_new_status(self, status):
        self.object.status = status
        self.object.save()

    def accept_invite(self):
        self.save_new_status(Invite.STATUS.accepted)

    def reject_invite(self):
        self.save_new_status(Invite.STATUS.rejected)

    def validate_invite(self):
        try:
            if Membership.objects.filter(
                community=self.request.community, member=self.request.user
            ).exists():
                raise ValidationError(_("You are already a member of this community."))
        except ValidationError as e:
            self.reject_invite()
            messages.error(self.request, e.message)  # noqa
            return redirect(self.get_redirect_url())
        return None


invite_accept_view = InviteAcceptView.as_view()
