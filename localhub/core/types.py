# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Custom type annotations for the project.
"""

from abc import abstractmethod

from typing import Any, Callable, Dict, List, Tuple, Type, Union, TYPE_CHECKING

from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from django.views.generic.base import ContextMixin

DjangoView = Callable[[HttpRequest], HttpResponse]

ContextDict = Dict[str, Any]

BreadcrumbList = List[Tuple[str, str]]

QuerySetDict = Dict[str, QuerySet]
QuerySetList = List[QuerySet]


ModelType = Type[Model]
ModelOrQuerySet = Union[ModelType, QuerySet]

ViewType = Type[View]


class _BaseQuerySetViewMixin:
    @abstractmethod
    def get_queryset(self) -> QuerySet:
        pass


if TYPE_CHECKING:
    BaseContextMixin = ContextMixin
    BaseQuerySetMixin = QuerySet
    BaseQuerySetViewMixin = _BaseQuerySetViewMixin
    BaseViewMixin = View
else:
    BaseContextMixin = object
    BaseQuerySetMixin = object
    BaseQuerySetViewMixin = object
    BaseViewMixin = object
