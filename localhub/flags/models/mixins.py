# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from localhub.db.generic import get_generic_related_exists

from . import Flag


class FlagAnnotationsQuerySetMixin:
    """
    Adds annotation methods to related model query set.
    """

    def with_is_flagged(self, annotated_name="is_flagged"):
        """
        Adds True if the object has been flagged by a user.
        """
        return self.annotate(
            **{annotated_name: get_generic_related_exists(self.model, Flag)}
        )

    def with_has_flagged(self, user, annotated_name="has_flagged"):
        """
        Adds True if the user in question has flagged the object.
        """
        return self.annotate(
            **{
                annotated_name: get_generic_related_exists(
                    self.model, Flag.objects.filter(user=user)
                )
            }
        )
