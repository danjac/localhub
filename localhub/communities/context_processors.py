from django.http import HttpRequest

from localhub.core.types import ContextDict


def community(request: HttpRequest) -> ContextDict:
    return {"community": request.community}
