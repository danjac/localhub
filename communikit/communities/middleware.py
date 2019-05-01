from django.http import HttpRequest, HttpResponse
from django.utils.functional import SimpleLazyObject

from communikit.communities.models import Community
from communikit.types import get_response_callable


class CurrentCommunityMiddleware:
    def __init__(self, get_response: get_response_callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.community = SimpleLazyObject(
            lambda: Community.objects.get_current(request)
        )
        return self.get_response(request)
