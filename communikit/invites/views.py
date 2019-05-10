from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, DeleteView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.models import Membership
from communikit.communities.views import CommunityRequiredMixin
from communikit.invites.forms import InviteForm
from communikit.invites.models import Invite
from communikit.types import ContextDict


class CommunityInviteQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Invite.objects.filter(community=self.request.community)


class InviteListView(
    LoginRequiredMixin,
    CommunityInviteQuerySetMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_required = "communities.manage_community"


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
    permission_required = "invites.create_invite"

    def get_form_kwargs(self) -> ContextDict:
        kwargs = super().get_form_kwargs()
        kwargs.update({"community": self.request.community})
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.sender = self.request.user
        self.object.community = self.request.community
        self.object.sent = timezone.utcnow()
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
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CommunityInviteQuerySetMixin,
    SingleObjectMixin,
    View,
):
    permission_required = "communities.manage_community"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=Invite.STATUS.pending)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.sent = timezone.utcnow()
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
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CommunityInviteQuerySetMixin,
    DeleteView,
):
    permission_required = "communities.manage_community"


invite_delete_view = InviteDeleteView.as_view()


class InviteAcceptView(CommunityRequiredMixin, SingleObjectMixin, View):
    """
    Click-thtorugh from link in email.

    If user is not logged in:
        - check if user with email address exists
        - if exists, redirect to login with ?redirect= back to this view
        - if not exists, redirect to signup with ?redirect= back here
    If user is logged in:
        - if another user matches email redirect to default
        - if user already belongs to community then just redirect to default
        - if user does not belong to the community then add the user as
          member and redirect to default
        "default" for now is just the content stream page.
    Flash message in all cases should differ based on situation.
    """

    allow_if_private = True

    def get_queryset(self) -> QuerySet:
        # TBD: add a deadline of e.g. 3 days
        return super().get_queryset().filter(status=Invite.STATUS.pending)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = (
            get_user_model()
            .filter(emailaddress__email__iexact=self.object.email)
            .first()
        )

        if not user:
            return self.handle_new_user()

        if request.user.is_anonymous:
            return self.handle_non_loggedin_user()

        if user == request.user:
            return self.handle_current_user()

        return self.handle_invalid_invite()

    def handle_new_user(self) -> HttpResponse:
        messages.info(self.request, _("Sign up to join this community"))
        redirect_url = (
            reverse("account_signup") + f"?redirect={self.request.path}"
        )
        return HttpResponseRedirect(redirect_url)

    def handle_logged_out_user(self) -> HttpResponse:
        messages.info(self.request, _("Login to join this community"))
        redirect_url = (
            reverse("account_login") + f"?redirect={self.request.path}"
        )
        return HttpResponseRedirect(redirect_url)

    def handle_current_user(self) -> HttpResponse:
        _membership, created = Membership.objects.get_or_create(
            member=self.request.user, community=self.request.community
        )

        if created:
            message = _("Welcome to %s") % self.request.community.name
        else:
            message = _("You are already a member of this community")

        messages.success(self.request, message)

        self.object.status = Invite.STATUS.accepted
        self.object.save()

        return HttpResponseRedirect(reverse("content:post_list"))

    def handle_invalid_invite(self) -> HttpResponse:
        messages.error(self.request, _("This invite is invalid"))

        self.object.status = Invite.STATUS.rejected
        self.object.save()

        return HttpResponseRedirect(reverse("content:post_list"))


invite_accept_view = InviteAcceptView.as_view()


def send_invitation_email(invite: Invite):
    # tbd: we'll use django-templated-mail at some point
    send_mail(
        _("Invitation to join"),
        loader.get_template("invites/emails/invitation.txt").render(
            {"invite": invite}
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{invite.community.domain}",
        [invite.email],
    )
