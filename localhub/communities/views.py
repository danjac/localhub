# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db.models import Count, OuterRef, Q, Subquery
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
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
        data["join_request"] = (
            self.request.user.is_authenticated
            and not is_member(self.request.user, self.request.community)
            and JoinRequest.objects.filter(
                sender=self.request.user, community=self.request.community
            )
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
        "google_tracking_id",
        "content_warning_tags",
        "listed",
        "allow_join_requests",
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
        return Community.objects.listed(self.request.user).order_by("name")

    def get_member_communities(self):
        return Community.objects.filter(
            membership__member=self.request.user, membership__active=True
        ).exclude(pk=self.request.community.id)

    def get_available_users(self):
        return (
            get_user_model()
            .objects.filter(is_active=True)
            .exclude(pk__in=self.request.user.blocked.all())
        )

    def get_notifications_count(self):
        return dict(
            self.get_member_communities()
            .annotate(
                num_notifications=Count(
                    "notification",
                    filter=Q(
                        notification__recipient=self.request.user,
                        notification__is_read=False,
                        notification__actor__pk__in=self.get_available_users(),
                        notification__actor__membership__active=True,
                    ),
                    distinct=True,
                )
            )
            .values_list("id", "num_notifications")
        )

    def get_messages_count(self):
        return dict(
            self.get_member_communities()
            .annotate(
                num_messages=Count(
                    "message",
                    filter=Q(
                        message__recipient=self.request.user,
                        message__read__isnull=True,
                        message__sender__pk__in=self.get_available_users(),
                        message__sender__membership__active=True,
                    ),
                    distinct=True,
                )
            )
            .values_list("id", "num_messages")
        )

    def get_join_requests_count(self):
        return dict(
            self.get_member_communities()
            .filter(membership__role=Membership.ROLES.admin)
            .annotate(
                num_join_requests=Count(
                    "joinrequest",
                    filter=Q(joinrequest__status=JoinRequest.STATUS.pending),
                    distinct=True,
                )
            )
            .values_list("id", "num_join_requests")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "join_requests_count": self.get_join_requests_count(),
                "messages_count": self.get_messages_count(),
                "notifications_count": self.get_notifications_count(),
            }
        )
        return data


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
    success_message = _("Membership has been updated")

    def get_success_url(self):
        return reverse("communities:membership_detail", args=[self.object.id])


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
