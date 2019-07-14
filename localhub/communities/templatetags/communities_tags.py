from django import template
from django.db.models import QuerySet

from localhub.communities.models import Community
from localhub.core.types import ContextDict

register = template.Library()


@register.simple_tag(takes_context=True)
def get_communities(context: ContextDict) -> QuerySet:
    """
    Returns list of communities a user belongs to
    """
    try:
        request = context["request"]
    except KeyError:
        return Community.objects.none()

    if request.user.is_anonymous:
        return Community.objects.none()

    # include inactive communities?

    return (
        Community.objects.filter(members=request.user)
        .order_by("name")
        .distinct()
    )
