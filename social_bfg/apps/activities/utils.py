# Standard Library
import collections

from .models import Activity


def get_activity_models():
    """
    Returns:
        list: all Activity subclasses
    """
    return Activity.__subclasses__()


def get_activity_models_dict():
    return {model._meta.model_name: model for model in get_activity_models()}


def get_activity_model(object_type):
    """
    Args:
        object_type (str): object model name e.g. "post"

    Returns:
        Activity model subclass
    """
    return get_activity_models_dict()[object_type]


def unionize_querysets(querysets, all=False):
    """Combines multiple querysets with single UNION statement.
    Columns must all be identical so remember to use with "only()".

    Args:
        querysets: iterable of Activity QuerySets
        all (bool, optional): whether to do UNION ALL (default: False)

    Returns:
        QuerySet -- combined QuerySet
    """
    return querysets[0].union(*querysets[1:], all=all)


def load_objects(items, querysets):
    """Loads objects from get_activity_querysets() into list of dict:

    union_qs, querysets = get_activity_querysets()
    load_objects(union_qs, querysets)

    [
        {

            "pk": 12345,
            "object_type": "post",
            "object": instance,
        }
    ...
    ]

    Args:
        items (iterable): individual dicts
        querysets (iterable): QuerySets for each Model class

    Returns:
        iterable: the original items along with key "object" containing
            the Model instance.
    """

    bulk_load = collections.defaultdict(set)

    for item in items:
        bulk_load[item["object_type"]].add(item["pk"])

    queryset_dict = {
        queryset.model._meta.model_name: queryset for queryset in querysets
    }

    fetched = {
        (object_type, obj.pk): obj
        for object_type, primary_keys in bulk_load.items()
        for obj in queryset_dict[object_type].filter(pk__in=primary_keys)
    }

    for item in items:
        item["object"] = fetched[(item["object_type"], item["pk"])]

    return items


def get_activity_querysets(queryset_fn, ordering=None, values=None, all=False):
    """Returns combined UNION queryset plus querysets for each Activity subclass.

    Args:
        queryset_fn: function taking argument of Activity model. Takes a Model
            class and returns a QuerySet.
        ordering (str, list, tuple, optional): ordering arguments for combined queryset.
        values (list, tuple, optional): columns to be returned. By
            default ("pk", "object_type")
        all (bool, optional): UNION ALL (default: False)

    Returns:
        A tuple consisting of union queryset, and list of individual querysets.
    """
    if isinstance(ordering, str):
        ordering = (ordering,)

    values = list(values) if values else ["pk", "object_type"]

    if ordering:
        values += [field.lstrip("-") for field in ordering]

    querysets = [queryset_fn(model) for model in get_activity_models()]

    qs = unionize_querysets(
        [qs.with_object_type().only(*values).values(*values) for qs in querysets],
        all=all,
    )

    if ordering:
        qs = qs.order_by(*ordering)

    return qs, querysets


def get_activity_queryset_count(queryset_fn):
    querysets = [queryset_fn(model).only("pk") for model in get_activity_models()]
    return unionize_querysets(querysets, all=True).count()
