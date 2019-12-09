# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.contrib.contenttypes.fields import GenericRelation

from localhub.comments.models import Comment
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification


class ActivityGenericRelations:

    """
    Usage:

    class Post(Activity):
        ActivityGenericRelations()

    adds following generic relations:

    post.comments
    post.flags
    post.notifications
    post.likes
    """

    def contribute_to_class(self, cls, name):

        relations = (
            (Comment, "comments"),
            (Flag, "flags"),
            (Like, "likes"),
            (Notification, "notifications"),
        )

        for model, relation_name in relations:
            relation = GenericRelation(model, related_query_name=cls._meta.model_name)
            relation.contribute_to_class(cls, relation_name)
