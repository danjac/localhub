from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, ListView, UpdateView

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.forms import MembershipForm
from communikit.communities.models import Community, Membership


class CommunityRequiredMixin:
    """
    Ensures that a community is available on this domain. This requires
    the CurrentCommunityMiddleware is enabled.

    If no community present raises a 404.

    TBD: we will need a specific route which lists available communities
    (if any). Instead of showing a 404, we redirect to this page.

    For example authentication routes (in emails etc) will be tied
    to the domain depending on SITE_ID, so if redirected there
    and no community matches that domain we need a page to allow user
    to select a community/request invite etc.

    TBD:

    @rules.predicate
    def is_public(community):
        return community.public

    rules.add_perm("communities.view_community", is_public | is_member)

    if not request.user.has_perm(
        request.community, "communities.view_community"):
        return HttpResponseRedirect(reverse("communities:request_access"))
    """

    # communities marked private would normally redirect to 403/membership
    # require page. The CommunityRequiredMixin flag allow_if_private on a view
    # skips this check, as we need to allow the user to accept the invite as
    # not yet a member.
    allow_if_private = False

    def dispatch(self, request, *args, **kwargs):
        if not request.community:
            raise Http404(_("No community is available for this domain"))
        return super().dispatch(request, *args, **kwargs)


class CommunityUpdateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    fields = ("name", "description", "public")

    permission_required = "communities.manage_community"
    success_message = _("Community settings have been updated")

    def get_object(self) -> Community:
        return self.request.community

    def get_success_url(self) -> str:
        return self.request.path


community_update_view = CommunityUpdateView.as_view()


class CommunityMembershipQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Membership.objects.filter(
            community=self.request.community
        ).select_related("community", "member")


class MembershipListView(
    LoginRequiredMixin,
    CommunityMembershipQuerySetMixin,
    PermissionRequiredMixin,
    ListView,
):
    paginate_by = 30
    allow_empty = True
    permission_required = "communities.manage_community"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("member__username")


membership_list_view = MembershipListView.as_view()


class MembershipUpdateView(
    LoginRequiredMixin,
    CommunityMembershipQuerySetMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    form_class = MembershipForm
    permission_required = "communities.change_membership"
    success_url = reverse_lazy("communities:membership_list")
    success_message = _("Membership has been updated")


membership_update_view = MembershipUpdateView.as_view()


class MembershipDeleteView(
    LoginRequiredMixin,
    CommunityMembershipQuerySetMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    fields = ("role", "active")
    permission_required = "communities.delete_membership"
    success_url = reverse_lazy("communities:membership_list")


membership_delete_view = MembershipDeleteView.as_view()
