from typing import List
from django.core.exceptions import ImproperlyConfigured


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
