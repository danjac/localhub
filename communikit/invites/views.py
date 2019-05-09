from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import _
from django.views.generic import CreateView, DetailView, ListView

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.views import CommunityRequiredMixin
from communikit.invites.forms import InviteForm
from communikit.invites.models import Invite
from communities.models import Membership


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
    form_class = InviteForm
    success_url = reverse_lazy("invites:list")
    permission_required = "invites.create_invite"

    def form_valid(self, form) -> HttpResponse:
        invite = form.save(commit=False)
        invite.sender = self.request.user
        invite.community = self.request.community
        invite.save()

        # send email to recipient

        return HttpResponseRedirect(self.get_success_url())


invite_create_view = InviteCreateView.as_view()


class InviteActionView(CommunityRequiredMixin, DetailView):
    template_name = "invites/action.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=Invite.STATUS.pending)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # tbd: check if user logged in...
        invite = self.get_object()
        # check if email belongs to user...
        # does this user exist? do this if not current user
        user = (
            get_user_model()
            .filter(email_addresses__email__iexact=invite.email)
            .first()
        )
        if user and request.user.is_authenticated and request.user != user:
            pass  # error page

        invite.status = (
            Invite.STATUS.rejected
            if "action_reject" in request.POST
            else Invite.STATUS.accepted
        )
        invite.save()
        redirect_url = reverse("content:list")

        if invite.status == Invite.STATUS.accepted:
            if user:
                Membership.objects.create(
                    member=user, community=invite.community
                )
                messages.success(_("You have been signed into...."))
                # if not auth, redirect to login page
            else:
                # redirect to page that
                redirect_url = reverse("account_signup") + "?redirect="
                messages.success(_("Please sign in to continue"))
        return HttpResponseRedirect(redirect_url)
