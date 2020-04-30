# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from localhub.db.generic import get_generic_related_count_subquery

from . import Comment


class CommentAnnotationsQuerySetMixin:
    """
    Adds comment-related annotation methods to a related model
    queryset.
    """

    def with_num_comments(self, community, annotated_name="num_comments"):
        """
        Annotates `num_comments` to the model.
        """
        return self.annotate(
            **{
                annotated_name: get_generic_related_count_subquery(
                    self.model, Comment.objects.for_community(community)
                )
            }
        )
