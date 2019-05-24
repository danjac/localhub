from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, DeleteView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.models import Community, Membership
from communikit.communities.views import CommunityRequiredMixin
from communikit.invites.emails import send_invitation_email
from communikit.invites.forms import InviteForm
from communikit.invites.models import Invite
from communikit.core.types import ContextDict


class CommunityInviteQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Invite.objects.filter(community=self.request.community)


class InviteListView(
    CommunityInviteQuerySetMixin,
    PermissionRequiredMixin,
    ListView,
):
    permission_required = "communities.manage_community"

    def get_permission_object(self) -> Community:
        return self.request.community


invite_list_view = InviteListView.as_view()


class InviteCreateView(
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
    PermissionRequiredMixin,
    CommunityInviteQuerySetMixin,
    SingleObjectMixin,
    View,
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
    PermissionRequiredMixin,
    CommunityInviteQuerySetMixin,
    DeleteView,
):
    permission_required = "communities.manage_community"
    success_url = reverse_lazy("invites:list")

    def get_permission_object(self) -> Community:
        return self.request.community


invite_delete_view = InviteDeleteView.as_view()


class InviteAcceptView(CommunityInviteQuerySetMixin, SingleObjectMixin, View):
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
            ._default_manager.filter(
                Q(emailaddress__email__iexact=self.object.email)
                | Q(email__iexact=self.object.email)
            )
            .first()
        )

        if not user:
            return self.handle_new_user()

        if request.user.is_anonymous:
            return self.handle_logged_out_user()

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

        return HttpResponseRedirect(settings.COMMUNIKIT_HOME_PAGE_URL)

    def handle_invalid_invite(self) -> HttpResponse:
        messages.error(self.request, _("This invite is invalid"))

        self.object.status = Invite.STATUS.rejected
        self.object.save()

        return HttpResponseRedirect(settings.COMMUNIKIT_HOME_PAGE_URL)


invite_accept_view = InviteAcceptView.as_view()
