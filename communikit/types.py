from typing import Any, Callable, Dict

from django.http import HttpRequest, HttpResponse

HttpRequestResponse = Callable[[HttpRequest], HttpResponse]

ContextDict = Dict[str, Any]
