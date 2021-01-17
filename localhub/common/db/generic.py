# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Functions for more efficient handling of ContentType related
objects with querysets.
"""

# Django
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AbstractGenericRelation:
    """
    Wraps GenericRelation. Allows setting a generic relation on abstract model
    and automatically setting related_query_name based on the concrete subclass.

    class Activity(Model):
        comments = AbstractGenericRelation(Comment)

    class Post(Activity):
        ...

    post.comments
    """

    def __init__(self, model):
        self.model = model

    def contribute_to_class(self, cls, name):
        relation = GenericRelation(self.model, related_query_name=cls._meta.model_name)
        relation.contribute_to_class(cls, name)


def get_generic_related_exists(
    model,
    related,
    related_object_id_field="object_id",
    related_content_type_field="content_type",
):
    """Used with QuerySet.annotate() to add an EXISTS clause
    to a QuerySet where you want to select based on a ContentType
    relation.

    For an example see LikesAnnotationQuerySetMixin in
    localhub.likes/models.py.

    Args:
        model (Model or Queryset): model class or QuerySet instance
        related (Model): ContentType-related model
        related_object_id_field (str, optional): field in content type model used as
            foreign key (default: "object_id")
        related_content_type_field (str, optional): field in content type model used
            as FK to ContentType (default: "content_type")

    Returns:
        Exists
    """
    return models.Exists(
        _get_generic_related_by_id_and_content_type(
            models.OuterRef("pk"),
            model,
            related,
            related_object_id_field,
            related_content_type_field,
        ).only("pk")
    )


def get_generic_related_count_subquery(
    model,
    related,
    related_object_id_field="object_id",
    related_content_type_field="content_type",
):
    """
    Used with QuerySet.annotate() to add a COUNT subquery
    to a QuerySet where you want to select based on a ContentType
    relation.

    For an example see LikesAnnotationQuerySetMixin in
    localhub.likes/models.py.

    Args:
        model (Model or Queryset): model class or QuerySet instance
        related (Model): ContentType-related model
        related_object_id_field (str, optional): field in content type model used as
            foreign key (default: "object_id")
        related_content_type_field (str, optional): field in content type model used
            as FK to ContentType (default: "content_type")

    Returns:
        Subquery
    """
    return models.Subquery(
        _get_generic_related_by_id_and_content_type(
            models.OuterRef("pk"),
            model,
            related,
            related_object_id_field,
            related_content_type_field,
        )
        .values(related_object_id_field)
        .annotate(count=models.Count("pk"))
        .values("count"),
        output_field=models.IntegerField(),
    )


def get_generic_related_value_subquery(
    model,
    related,
    field,
    output_field,
    related_object_id_field="object_id",
    related_content_type_field="content_type",
):
    """
    Returns a selected field in Subquery. Use with caution with non-unique
    rows!

    Args:
        model (Model or Queryset): model class or QuerySet instance
        related (Model): ContentType-related model
        field (str): field name to map
        output_field (Field): output field e.g. models.CharField()
        related_object_id_field (str, optional): field in content type model used as
            foreign key (default: "object_id")
        related_content_type_field (str, optional): field in content type model used
            as FK to ContentType (default: "content_type")

    Returns:
        Subquery
    """
    return models.Subquery(
        _get_generic_related_by_id_and_content_type(
            models.OuterRef("pk"),
            model,
            related,
            related_object_id_field,
            related_content_type_field,
        ).values(field),
        output_field=output_field,
    )


def get_generic_related_queryset(
    model_or_queryset,
    related,
    related_object_id_field="object_id",
    related_content_type_field="content_type",
):
    """
    Used inside a model instance to provide all instances
    of a related content type matching the object's primary key.

    Args:
        model (Model or Queryset): Model or QuerySet instance
        related (Model): ContentType-related model
        related_object_id_field (str, optional): field in content type model used as
            foreign key (default: "object_id")
        related_content_type_field (str, optional): field in content type model used
            as FK to ContentType (default: "content_type")

    Returns:
        QuerySet
    """

    if isinstance(model_or_queryset, models.QuerySet):
        lookup_value = model_or_queryset.values("pk")
        related_object_id_field = f"{related_object_id_field}__in"
    else:
        lookup_value = model_or_queryset.pk

    return _get_generic_related_by_id_and_content_type(
        lookup_value,
        model_or_queryset,
        related,
        related_object_id_field,
        related_content_type_field,
    )


def _get_generic_related_by_id_and_content_type(
    lookup_value,
    model_or_queryset,
    related,
    related_object_id_field="object_id",
    related_content_type_field="content_type",
):

    if isinstance(model_or_queryset, models.QuerySet):
        model = model_or_queryset.model
    else:
        model = model_or_queryset
    return _get_queryset(related).filter(
        **{
            related_object_id_field: lookup_value,
            related_content_type_field: ContentType.objects.get_for_model(model),
        }
    )


def _get_queryset(model_or_queryset):
    return (
        model_or_queryset
        if isinstance(model_or_queryset, models.QuerySet)
        else model_or_queryset._default_manager.all()
    )
