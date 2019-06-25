from typing import Optional

from communikit.core.types import BreadcrumbList, ContextDict


class BreadcrumbsMixin:
    breadcrumbs: Optional[BreadcrumbList] = None

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.breadcrumbs or []

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data()
        data["breadcrumbs"] = self.get_breadcrumbs()
        return data
