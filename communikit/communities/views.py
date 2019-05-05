from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.models import Community


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

    def dispatch(self, request, *args, **kwargs):
        if not request.community:
            raise Http404(_("No community is available for this domain"))
        return super().dispatch(request, *args, **kwargs)


class CommunityUpdateView(
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    fields = ("name", "description", "public")

    permission_required = "communities.change_community"
    success_message = _("Community settings have been updated")

    def get_object(self) -> Community:
        return self.request.community

    def get_success_url(self):
        return self.request.path


community_update_view = CommunityUpdateView.as_view()
