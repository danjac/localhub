from django import template
from django.conf import settings
from django.db.models import QuerySet

from localhub.communities.models import Community

register = template.Library()


@register.simple_tag
def get_local_communities(
    user: settings.AUTH_USER_MODEL, community: Community
) -> QuerySet:
    """
    Returns other communities on same host belonging to this user.
    """
    if user.is_anonymous:
        return Community.objects.none()

    qs = (
        Community.objects.filter(members=user, active=True)
        .order_by("name")
        .distinct()
    )

    if community.id:
        qs = qs.exclude(pk=community.id)
    return qs
