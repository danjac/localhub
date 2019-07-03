# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Any, Union

from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    Count,
    Exists,
    IntegerField,
    Model,
    OuterRef,
    Subquery,
    QuerySet,
)

from communikit.core.types import ModelClass, ModelOrQuerySet


def get_generic_related_exists(
    model: ModelClass,
    related: ModelOrQuerySet,
    related_object_id_field: str = "object_id",
    related_content_type_field: str = "content_type",
) -> Exists:
    return Exists(
        _get_generic_related_by_id_and_content_type(
            OuterRef("pk"),
            model,
            related,
            related_object_id_field,
            related_content_type_field,
        )
    )


def get_generic_related_count_subquery(
    model: ModelClass,
    related: ModelOrQuerySet,
    related_object_id_field: str = "object_id",
    related_content_type_field: str = "content_type",
) -> Subquery:
    return Subquery(
        _get_generic_related_by_id_and_content_type(
            OuterRef("pk"),
            model,
            related,
            related_object_id_field,
            related_content_type_field,
        )
        .values(related_object_id_field)
        .annotate(count=Count("pk"))
        .values("count"),
        output_field=IntegerField(),
    )


def get_generic_related_queryset(
    model: Model,
    related: ModelOrQuerySet,
    related_object_id_field: str = "object_id",
    related_content_type_field: str = "content_type",
) -> QuerySet:
    return _get_generic_related_by_id_and_content_type(
        model.pk,
        model,
        related,
        related_object_id_field,
        related_content_type_field,
    )


def _get_generic_related_by_id_and_content_type(
    pk: Any,
    model: Union[ModelClass, Model],
    related: ModelOrQuerySet,
    related_object_id_field: str = "object_id",
    related_content_type_field: str = "content_type",
) -> QuerySet:

    return _get_queryset(related).filter(
        **{
            related_object_id_field: pk,
            related_content_type_field: ContentType.objects.get_for_model(
                model
            ),
        }
    )


def _get_queryset(model_or_queryset: ModelOrQuerySet) -> QuerySet:
    return (
        model_or_queryset
        if isinstance(model_or_queryset, QuerySet)
        else model_or_queryset._default_manager.all()
    )
