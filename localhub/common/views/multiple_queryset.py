# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections import defaultdict

from django.db.models import CharField, Value

from vanilla import TemplateView

from localhub.common.pagination import PresetCountPaginator


class MultipleQuerySetMixin:
    """
    An efficient approach to combining multiple querysets
    from different models into a single QuerySet that can be rendered
    in a view. SQL UNION is used to combine the querysets into a single
    SQL query.

    If ordering/pagination is used, the querysets must share the same
    ordering field names. For example, if you wish to set the ordering
    by "-created" then all models in all the querysets must have a
    "created" field (or create one as an annotation).

    Each model instance returned from the combined queryset will include
    an `object_type` annotation (same as the model's Meta.model_name) that
    can be used in templates and elsewhere to handle display logic specific
    to that model e.g.

    {% for item in object_list %}
    {% if item.object_type == "post" %}
    {# do Post specific content... #}

    The method `get_querysets` must be implemented by returning a list
    of QuerySet instances.

    Pagination is handled in same way as for ListView, i.e. just set the
    `paginate_by` variable.

    For a complete example see BaseStreamView in
    localhub/activities/views/streams.py.

    Pattern adapted from:
    https://simonwillison.net/2018/Mar/25/combined-recent-additions/
    """

    allow_empty = True
    limit = None
    ordering = None
    paginate_by = None
    paginator_class = PresetCountPaginator
    page_kwarg = "page"

    def get_querysets(self):
        """
        This must be implemented by returning a list of QuerySets, one
        for each different model.
        """
        raise NotImplementedError

    def get_ordering(self):
        return self.ordering

    def get_queryset_dict(self):
        return {
            queryset.model._meta.model_name: queryset
            for queryset in self.get_querysets()
        }

    def get_count_querysets(self):
        return self.get_querysets()

    def get_combined_count_queryset(self):
        querysets = [qs.only("pk") for qs in self.get_count_querysets()]
        return querysets[0].union(*querysets[1:], all=True)

    def get_combined_count(self):
        return self.get_combined_count_queryset().count()

    def get_combined_queryset(self, queryset_dict):
        values = ["pk", "object_type"]

        ordering = self.get_ordering()
        if isinstance(ordering, str):
            ordering = (ordering,)

        if ordering:
            values += [field.lstrip("-") for field in ordering]

        querysets = [
            qs.annotate(object_type=Value(key, output_field=CharField())).values(
                *values
            )
            for key, qs in queryset_dict.items()
        ]
        qs = querysets[0].union(*querysets[1:])
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def load_objects(self, items, queryset_dict):
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

    def get_object_list(self):

        queryset_dict = self.get_queryset_dict()
        union_qs = self.get_combined_queryset(queryset_dict)
        if self.limit:
            union_qs = union_qs[: self.limit]

        self.load_objects(union_qs, queryset_dict)
        return union_qs

    def get_page(self):
        queryset_dict = self.get_queryset_dict()
        union_qs = self.get_combined_queryset(queryset_dict)

        page = self.paginator_class(
            object_list=union_qs,
            count=self.get_combined_count(),
            **self.get_pagination_kwargs()
        ).get_page(self.request.GET.get(self.page_kwarg, 1))

        self.load_objects(page, queryset_dict)

        return page

    def get_pagination_kwargs(self):
        return {
            "per_page": self.paginate_by,
            "allow_empty_first_page": self.allow_empty,
        }


class BaseMultipleQuerySetListView(MultipleQuerySetMixin, TemplateView):
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.paginate_by:
            page = self.get_page()
            data.update(
                {
                    "page_obj": page,
                    "paginator": page.paginator,
                    "object_list": page.object_list,
                    "is_paginated": page.has_other_pages(),
                }
            )
        else:
            data.update({"object_list": self.get_object_list()})
        return data
