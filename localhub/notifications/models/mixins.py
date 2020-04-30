# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from localhub.common.db.generic import get_generic_related_exists
from localhub.common.db.utils import boolean_value

from . import Notification


class NotificationAnnotationsQuerySetMixin:
    """
    Annotation methods for related model query sets.
    """

    def with_is_new(self, recipient, annotated_name="is_new"):
        """Annotates "is_new" to queryset if notification(s) unread for
        this object.

        Args:
            recipient (User)
            annotated_name (str, optional): the annotation name (default: "is_new")

        Returns:
            QuerySet
        """
        return self.annotate(
            **{
                annotated_name: boolean_value(False)
                if recipient.is_anonymous
                else get_generic_related_exists(
                    self.model,
                    Notification.objects.filter(is_read=False, recipient=recipient),
                )
            }
        )
