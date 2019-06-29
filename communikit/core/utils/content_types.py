# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

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


def get_content_type_exists(
    content_type_model: Model,
    queryset: QuerySet,
    object_id_field: str = "object_id",
    content_type_field: str = "content_type",
) -> Exists:
    return Exists(
        queryset.filter(
            **{
                object_id_field: OuterRef("pk"),
                content_type_field: ContentType.objects.get_for_model(
                    content_type_model
                ),
            }
        )
    )


def get_content_type_count_subquery(
    content_type_model: Model,
    queryset: QuerySet,
    object_id_field: str = "object_id",
    content_type_field: str = "content_type",
) -> Subquery:
    return Subquery(
        queryset.filter(
            **{
                object_id_field: OuterRef("pk"),
                content_type_field: ContentType.objects.get_for_model(
                    content_type_model
                ),
            }
        )
        .values(object_id_field)
        .annotate(count=Count("pk"))
        .values("count"),
        output_field=IntegerField(),
    )
