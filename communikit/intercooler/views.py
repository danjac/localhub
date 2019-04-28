from typing import List

from django.http import HttpRequest, HttpResponse
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import DeleteView


class IntercoolerTemplateMixin:
    """
    If Intercooler header is present then uses ic_template_name
    instead of usual template.

    IntercoolerRequestMiddleware must be enabled.
    """

    ic_template_name = None

    def get_template_names(self) -> List[str]:
        if self.request.is_intercooler():
            if self.ic_template_name is None:
                raise ImproperlyConfigured("ic_template_name must be defined")
            return [self.ic_template_name]
        return super().get_template_names()


class IntercoolerDeletionMixin:
    """
    If Intercooler request and target id will pass back the X-IC-Remove
    header

    IntercoolerRequestMiddleware must be enabled.
    """
    removal_delay = "500ms"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.is_intercooler() and request.intercooler_data.target_id:
            self.get_object().delete()
            response = HttpResponse()
            response["X-IC-Remove"] = self.removal_delay
            return response
        return super().delete(request, *args, **kwargs)


class IntercoolerDeleteView(IntercoolerDeletionMixin, DeleteView):
    pass
