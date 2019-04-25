from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.utils.functional import SimpleLazyObject

from communikit.communities.models import Community


class CurrentCommunityMiddleware:
    """
    Requires Site middleware be enabled before this middleware:
    https://docs.djangoproject.com/en/2.2/ref/middleware/#django.contrib.sites.middleware.CurrentSiteMiddleware
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.community = SimpleLazyObject(
            lambda: Community.objects.get_current(request)
        )
        return self.get_response(request)
