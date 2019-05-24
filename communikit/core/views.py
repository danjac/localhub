# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List

from collections import defaultdict

from django.core.paginator import Page, Paginator
from django.db.models import CharField, QuerySet, Value
from django.views.generic import TemplateView

from communikit.core.types import ContextDict


QuerySetDict = Dict[str, QuerySet]


class CombinedQuerySetMixin:
    """
    Pattern adapted from:
    https://simonwillison.net/2018/Mar/25/combined-recent-additions/
    """
    order_field = None
    paginate_by = None
    allow_empty = True
    limit = None

    def get_querysets(self) -> List[QuerySet]:
        return []

    def get_order_field(self) -> str:
        return self.order_field

    def get_queryset_dict(self) -> QuerySetDict:
        return {
            queryset.model._meta.model_name: queryset
            for queryset in self.get_querysets()
        }

    def get_combined_queryset(self, queryset_dict: QuerySetDict) -> QuerySet:
        values = ["pk", "object_type"]

        order_field = self.get_order_field()

        if order_field:
            values.append(order_field)

        querysets = [
            qs.annotate(
                object_type=Value(key, output_field=CharField())
            ).values(*values)
            for key, qs in queryset_dict.items()
        ]
        qs = querysets[0].union(*querysets[1:])
        if order_field:
            qs = qs.order_by(f"-{order_field}")
        return qs

    def load_objects(self, items: QuerySet, queryset_dict: QuerySetDict):
        bulk_load = defaultdict(set)

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

        self.load_objects(union_qs)
        return union_qs

    def get_page(self) -> Page:
        queryset_dict = self.get_queryset_dict()
        union_qs = self.get_combined_queryset(queryset_dict)

        page = Paginator(union_qs, **self.get_pagination_kwargs()).get_page(
            self.request.GET.get("page", 1)
        )

        self.load_objects(page, queryset_dict)

        return page

    def get_pagination_kwargs(self) -> ContextDict:
        return {
            "per_page": self.paginate_by,
            "allow_empty_first_page": self.allow_empty,
        }


class CombinedQuerySetContextMixin(CombinedQuerySetMixin):
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


class CombinedQuerySetListView(CombinedQuerySetContextMixin, TemplateView):
    pass
