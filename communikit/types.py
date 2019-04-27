from typing import Callable

from django.http import HttpRequest, HttpResponse

get_response_callable = Callable[[HttpRequest], HttpResponse]
