# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.template.defaultfilters import truncatechars
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from localhub.comments.models import Comment
from localhub.notifications.models import Notification
from localhub.notifications.utils import send_push_notification

NOTIFICATION_HEADS = {
    "flag": _("%(actor)s has flagged this comment"),
    "like": _("%(actor)s has liked your comment"),
    "mention": _("%(actor)s has mentioned you in their comment"),
    "moderator_edit": _("A moderator has edited your comment"),
    "moderator_review_request": _(
        "%(actor)s has submitted a new comment to review"
    ),
    "new_comment": _("%(actor)s has submitted a comment on one of your posts"),
    "new_sibling_comment": _(
        "%(actor)s has made a comment on a post you've commented on"
    ),
    "new_followed_user_comment": _("%(actor)s has submitted a new comment"),
}


def send_comment_notification_push(
    comment: Comment, notification: Notification
):
    with override(notification.recipient.language):

        send_push_notification(
            notification.recipient,
            notification.community,
            head=NOTIFICATION_HEADS[notification.verb]
            % {"actor": notification.actor},
            body=force_text(truncatechars(comment.content, 60)),
            url=comment.get_permalink(),
        )
