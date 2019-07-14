# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional

from localhub.core.types import BreadcrumbList, ContextDict


class BreadcrumbsMixin:
    """
    View mixin providing a list of (url, label) tuples
    that can be rendered with the appropriate HTML component.

    The list is inserted into the template context with the key "breadcrumbs".

    Example:

    class MyView(BreadcrumbsMixin, TemplateView):

        def get_breadcrumbs(self):
            return [
                ("/", _("Home")),
                (self.request.path, _("Here")),
            ]

    In template:
    {% for url, label in breadcrumbs %}
    <li class="breadcrumb"><a href="{{ url }}">{{ label }}</a></li>
    {% endfor %}
    """

    breadcrumbs: Optional[BreadcrumbList] = None

    def get_breadcrumbs(self) -> BreadcrumbList:
        """
        Returns list of (url/label) tuples. Override as required.
        """
        return self.breadcrumbs or []

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data()
        data["breadcrumbs"] = self.get_breadcrumbs()
        return data
