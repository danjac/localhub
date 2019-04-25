from django.http import Http404
from django.utils.functional import ugettext_lazy as _


class CommunityRequiredMixin:
    """
    Ensures that a community is available on this domain. This requires
    the CurrentCommunityMiddleware is enabled.

    If no community present raises a 404.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.community:
            raise Http404(_("No community is available for this domain"))
        return super().dispatch(request, *args, **kwargs)
