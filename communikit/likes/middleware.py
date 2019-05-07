import collections

from django.db.models import Model
from django.http import HttpRequest, HttpResponse

from communikit.likes.models import Like
from communikit.types import HttpRequestResponse


def _has_liked(self, obj: Model) -> bool:
    if self.user.is_anonymous:
        return False
    if not hasattr(self, "_likes"):
        self._likes = collections.defaultdict(set)
        for like in Like.objects.filter(user=self.request.user).select_related(
            "content_type"
        ):
            self._likes[like.content_type.name].add(like.object_id)
    try:
        return self._likes[obj._meta.verbose_name] == obj.id
    except KeyError:
        return False


class LikesMiddleware:
    def __init__(self, get_response: HttpRequestResponse):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.has_liked = _has_liked.__get__(request)
        return self.get_response(request)
