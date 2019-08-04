from django import template
from django.conf import settings

from localhub.communities.models import Community

register = template.Library()


@register.simple_tag
def get_local_communities_count(
    user: settings.AUTH_USER_MODEL, community: Community
) -> int:
    """
    Returns other communities on same host belonging to this user.
    """

    qs = Community.objects.available(user)
    if community.id:
        qs = qs.exclude(pk=community.id)

    return qs.count()
