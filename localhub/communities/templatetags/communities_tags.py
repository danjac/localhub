from django import template
from django.conf import settings
from django.db.models import Q, QuerySet

from localhub.communities.models import Community

register = template.Library()


@register.simple_tag
def get_local_communities(
    user: settings.AUTH_USER_MODEL, community: Community
) -> QuerySet:
    """
    Returns other communities on same host belonging to this user.
    """

    qs = Community.objects.filter(active=True)
    if user.is_anonymous:
        qs = qs.filter(public=True)
    else:
        qs = qs.filter(Q(public=True) | Q(members=user))
    if community.id:
        qs = qs.exclude(pk=community.id)

    return qs.order_by("name").distinct()
