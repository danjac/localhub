# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from localhub.activities.models import Activity
from localhub.notifications.models import Notification
from localhub.notifications.utils import send_push_notification

NOTIFICATION_HEADS = {
    "flag": _("%(actor)s has flagged this %(activity)s"),
    "like": _("%(actor)s has liked your %(activity)s"),
    "mention": _("%(actor)s has mentioned you in their %(activity)s"),
    "moderator_edit": _("A moderator has edited your %(activity)s"),
    "moderator_review_request": _(
        "%(actor)s has submitted a new %(activity)s to review"
    ),
    "new_followed_user_post": _("%(actor)s has submitted a new %(activity)s"),
    "new_followed_user_tag": _(
        "Someone has submitted a new %(activity)s containing "
        "tags you are following"
    ),
    "reshare": _("%(actor)s has reshared your %(activity)s"),
}


def send_activity_notification_push(
    activity: Activity, notification: Notification
):
    with override(notification.recipient.language):

        send_push_notification(
            notification.recipient,
            head=NOTIFICATION_HEADS[notification.verb]
            % {
                "actor": notification.actor,
                "activity": activity._meta.verbose_name,
            },
            body=force_text(activity),
            url=activity.get_permalink(),
        )
