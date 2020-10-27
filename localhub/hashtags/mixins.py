# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import operator
from functools import reduce

# Django
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

# Third Party Libraries
from taggit.models import Tag, TaggedItem

# Localhub
from localhub.activities.utils import get_activity_models
from localhub.communities.mixins import CommunityRequiredMixin


class TagQuerySetMixin(CommunityRequiredMixin):

    model = Tag

    # if True, only those tags used in this community by activities
    # will be included
    exclude_unused_tags = False

    def get_tagged_items(self):
        q = Q(
            reduce(
                operator.or_,
                [
                    Q(
                        object_id__in=model.objects.filter(
                            community=self.request.community
                        ).values("id"),
                        content_type=content_type,
                    )
                    for model, content_type in ContentType.objects.get_for_models(
                        *get_activity_models()
                    ).items()
                ],
            )
        )
        return TaggedItem.objects.filter(q)

    def get_queryset(self):
        if self.exclude_unused_tags:
            return Tag.objects.filter(
                taggit_taggeditem_items__in=self.get_tagged_items()
            ).distinct()
        return super().get_queryset()
