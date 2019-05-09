from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, DetailView, ListView

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
        self.object.save()

        # send email to recipient
        template = loader.get_template("invites/emails/invitation.txt")

        send_mail(
            _("Invitation to join"),
            template.render({"invite": self.object}),
            "from@example.com",
            [self.object.email],
        )

        messages.success(
            self.request,
            _("Your invitation has been sent to %s") % self.object.email,
        )

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
