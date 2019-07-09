# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Custom type annotations for the project.
"""

from typing import Any, Callable, Dict, List, Tuple, Type, Union

from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.views.generic import View

DjangoView = Callable[[HttpRequest], HttpResponse]

ContextDict = Dict[str, Any]

BreadcrumbList = List[Tuple[str, str]]

QuerySetDict = Dict[str, QuerySet]
QuerySetList = List[QuerySet]


ModelType = Type[Model]
ModelOrQuerySet = Union[ModelType, QuerySet]

ViewType = Type[View]
