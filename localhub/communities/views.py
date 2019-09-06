# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import LoginForm

from rules.contrib.views import PermissionRequiredMixin

from vanilla import DeleteView, DetailView, ListView, TemplateView, UpdateView

from localhub.communities.emails import send_membership_deleted_email
from localhub.communities.forms import MembershipForm
from localhub.communities.models import Community, Membership
from localhub.communities.rules import is_member
from localhub.common.views import SearchMixin
from localhub.join_requests.models import JoinRequest


class CommunityRequiredMixin:
    """
    Ensures that a community is available on this domain. This requires
    the CurrentCommunityMiddleware is enabled.

    If the user is not a member they will be redirected to the Welcome view.

    If the view has the `allow_non_members` property *True* then the above
    rule is overriden - for example in some cases where we want to allow
    the user to be able to handle an invitation.
    """

    allow_non_members = False

    def dispatch(self, request, *args, **kwargs):
        if not request.community.active:
            return self.handle_community_not_found()

        if (
            not request.user.has_perm(
                "communities.view_community", request.community
            )
            and not self.allow_non_members
        ):
            return self.handle_community_access_denied()
        return super().dispatch(request, *args, **kwargs)

    def handle_community_access_denied(self):
        if self.request.is_ajax():
            raise PermissionDenied(_("You must be a member of this community"))
        return HttpResponseRedirect(reverse("community_welcome"))

    def handle_community_not_found(self):
        if self.request.is_ajax():
            raise Http404(_("No community is available for this domain"))
        return HttpResponseRedirect(reverse("community_not_found"))


class MembershipQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Membership.objects.filter(
            community=self.request.community
        ).select_related("community", "member")


class CommunityDetailView(CommunityRequiredMixin, DetailView):
    model = Community

    def get_object(self):
        return self.request.community


community_detail_view = CommunityDetailView.as_view()


class CommunityTermsView(CommunityDetailView):
    template_name = "communities/terms.html"


community_terms_view = CommunityTermsView.as_view()


class CommunityNotFoundView(TemplateView):
    """
    This is shown if no community exists for this domain.
    """

    template_name = "communities/not_found.html"


community_not_found_view = CommunityNotFoundView.as_view()


class CommunityWelcomeView(CommunityRequiredMixin, TemplateView):
    """
    This is shown if the user is not a member (or is not authenticated).

    If user is already a member, redirects to home page.
    """

    template_name = "communities/welcome.html"
    allow_non_members = True

    def get(self, request, *args, **kwargs):
        if is_member(request.user, request.community):
            return HttpResponseRedirect(settings.HOME_PAGE_URL)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["join_request_sent"] = (
            self.request.user.is_authenticated
            and not is_member(self.request.user, self.request.community)
            and JoinRequest.objects.filter(
                sender=self.request.user,
                community=self.request.community,
                status=JoinRequest.STATUS.pending,
            ).exists()
        )
        if self.request.user.is_anonymous:
            data["login_form"] = LoginForm()
        return data


community_welcome_view = CommunityWelcomeView.as_view()


class CommunityUpdateView(
    CommunityRequiredMixin, PermissionRequiredMixin, UpdateView
):
    fields = (
        "name",
        "logo",
        "tagline",
        "intro",
        "description",
        "terms",
        "content_warning_tags",
        "blacklisted_email_domains",
        "blacklisted_email_addresses",
    )

    permission_required = "communities.manage_community"
    success_message = _("Community settings have been updated")
    model = Community

    def get_object(self):
        return self.request.community

    def get_success_url(self):
        return self.request.path

    def get_success_message(self):
        return self.success_message

    def form_valid(self, form: ModelForm):
        community = form.save(commit=False)
        community.admin = self.request.user
        community.save()
        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


community_update_view = CommunityUpdateView.as_view()


class CommunityListView(LoginRequiredMixin, SearchMixin, ListView):
    """
    Returns all public communities, or communities the
    current user belongs to.
    """

    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_template_names(self):
        if self.request.community and is_member(
            self.request.user, self.request.community
        ):
            return ["communities/member_community_list.html"]
        return ["communities/non_member_community_list.html"]

    def get_queryset(self):
        qs = (
            Community.objects.filter(active=True)
            .with_num_members()
            .with_is_member(self.request.user)
            .order_by("name")
        )
        if self.search_query:
            qs = qs.filter(name__icontains=self.search_query)
        return qs


community_list_view = CommunityListView.as_view()


class MembershipListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    MembershipQuerySetMixin,
    SearchMixin,
    ListView,
):
    paginate_by = settings.DEFAULT_PAGE_SIZE
    permission_required = "communities.manage_community"
    model = Membership

    def get_permission_object(self):
        return self.request.community

    def get_queryset(self):

        qs = (
            super().get_queryset().order_by("member__name", "member__username")
        )

        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


membership_list_view = MembershipListView.as_view()


class MembershipDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    MembershipQuerySetMixin,
    DetailView,
):

    permission_required = "communities.view_membership"
    model = Membership


membership_detail_view = MembershipDetailView.as_view()


class MembershipUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    MembershipQuerySetMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Membership
    form_class = MembershipForm
    permission_required = "communities.change_membership"
    success_url = reverse_lazy("communities:membership_list")
    success_message = _("Membership has been updated")


membership_update_view = MembershipUpdateView.as_view()


class MembershipDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    MembershipQuerySetMixin,
    DeleteView,
):
    permission_required = "communities.delete_membership"
    model = Membership

    def get_success_url(self):
        if self.object.member == self.request.user:
            return settings.HOME_PAGE_URL
        return reverse("communities:membership_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(
            self.request,
            _("Membership for user %s has been deleted")
            % self.object.member.username,
        )
        send_membership_deleted_email(
            self.object.member, self.object.community
        )
        return HttpResponseRedirect(self.get_success_url())


membership_delete_view = MembershipDeleteView.as_view()


class CommunityLeaveView(MembershipDeleteView):
    """
    Allows the current user to be able to leave the community.
    """

    template_name = "communities/leave.html"

    def get_object(self):
        return (
            super()
            .get_queryset()
            .filter(member__pk=self.request.user.id)
            .get()
        )

    def get_success_url(self):
        return settings.HOME_PAGE_URL


community_leave_view = CommunityLeaveView.as_view()
