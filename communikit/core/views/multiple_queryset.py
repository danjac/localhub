# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections import defaultdict

from typing import Optional, DefaultDict, Set

from django.core.paginator import Page, Paginator
from django.db.models import CharField, QuerySet, Value
from django.http import HttpRequest
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin

from communikit.core.types import ContextDict, QuerySetDict, QuerySetList


class MultipleQuerySetMixin:
    """
    Pattern adapted from:
    https://simonwillison.net/2018/Mar/25/combined-recent-additions/
    """

    allow_empty = True
    limit: Optional[int] = None
    ordering: Optional[str] = None
    paginate_by: Optional[int] = None
    page_kwarg = "page"
    request: HttpRequest

    def get_querysets(self) -> QuerySetList:
        raise NotImplementedError

    def get_ordering(self) -> Optional[str]:
        return self.ordering

    def get_queryset_dict(self) -> QuerySetDict:
        return {
            queryset.model._meta.model_name: queryset
            for queryset in self.get_querysets()
        }

    def get_combined_queryset(self, queryset_dict: QuerySetDict) -> QuerySet:
        values = ["pk", "object_type"]

        ordering = self.get_ordering()

        if ordering:
            values.append(ordering)

        querysets = [
            qs.annotate(
                object_type=Value(key, output_field=CharField())
            ).values(*values)
            for key, qs in queryset_dict.items()
        ]
        qs = querysets[0].union(*querysets[1:])
        if ordering:
            qs = qs.order_by(f"-{ordering}")
        return qs

    def load_objects(self, items: QuerySet, queryset_dict: QuerySetDict):
        bulk_load: DefaultDict[str, Set] = defaultdict(set)

        for item in items:
            bulk_load[item["object_type"]].add(item["pk"])

        fetched = {
            (object_type, obj.pk): obj
            for object_type, pks in bulk_load.items()
            for obj in queryset_dict[object_type].filter(pk__in=pks)
        }

        for item in items:
            item["object"] = fetched[(item["object_type"], item["pk"])]

    def get_object_list(self) -> QuerySet:

        queryset_dict = self.get_queryset_dict()
        union_qs = self.get_combined_queryset(queryset_dict)
        if self.limit:
            union_qs = union_qs[: self.limit]

        self.load_objects(union_qs, queryset_dict)
        return union_qs

    def get_page(self) -> Page:
        queryset_dict = self.get_queryset_dict()
        union_qs = self.get_combined_queryset(queryset_dict)

        page = Paginator(union_qs, **self.get_pagination_kwargs()).get_page(
            self.request.GET.get(self.page_kwarg, 1)
        )

        self.load_objects(page, queryset_dict)

        return page

    def get_pagination_kwargs(self) -> ContextDict:
        return {
            "per_page": self.paginate_by,
            "allow_empty_first_page": self.allow_empty,
        }


class MultipleQuerySetContextMixin(MultipleQuerySetMixin, ContextMixin):
    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        if self.paginate_by:
            page = self.get_page()
            data.update(
                {
                    "page": page,
                    "paginator": page.paginator,
                    "object_list": page.object_list,
                    "is_paginated": page.has_other_pages(),
                }
            )
        else:
            data.update({"object_list": self.get_object_list()})
        return data


class MultipleQuerySetListView(MultipleQuerySetContextMixin, TemplateView):
    ...
