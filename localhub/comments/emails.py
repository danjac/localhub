# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from localhub.comments.models import Comment
from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification


def send_comment_deleted_email(comment: Comment):
    context = {"comment": comment}
    send_mail(
        _("Your comment has been deleted by a moderator"),
        render_to_string("comments/emails/comment_deleted.txt", context),
        comment.community.resolve_email("notifications"),
        [comment.owner.email],
        html_message=render_to_string(
            "comments/emails/comment_deleted.html", context
        ),
    )


def send_comment_notification_email(
    comment: Comment, notification: Notification
):

    SUBJECTS = {
        "mentioned": _("Someone has mentioned you in their comment"),
        "created": _("Someone has published a new comment"),
        "commented": _("Someone has made a comment on one of your posts"),
        "updated": _("Someone has updated their comment"),
        "flagged": _("Someone has flagged this comment"),
    }

    send_notification_email(
        notification,
        SUBJECTS[notification.verb],
        comment.get_permalink(),
        "comments/emails/notification.txt",
        "comments/emails/notification.html",
        {"comment": comment},
    )
