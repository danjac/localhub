# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from localhub.comments.models import Comment
from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification


NOTIFICATION_PREFERENCES = {
    "comment": "comments",
    "delete": "deletes",
    "edit": "edits",
    "flag": "flags",
    "like": "likes",
    "mention": "mentions",
    "review": "reviews",
}

NOTIFICATION_SUBJECTS = {
    "comment": _("Someone has made a comment on one of your posts"),
    "delete": _("Your comment has been deleted by a moderator"),
    "edit": _("A moderator has edited your comment"),
    "flag": _("Someone has flagged this comment"),
    "like": _("Someone has liked your comment"),
    "mention": _("Someone has mentioned you in their comment"),
    "review": _("Someone has posted or updated a comment to review"),
}


def send_comment_notification_email(
    comment: Comment, notification: Notification
):

    if notification.recipient.has_email_pref(
        NOTIFICATION_PREFERENCES[notification.verb]
    ):

        send_notification_email(
            notification,
            NOTIFICATION_SUBJECTS[notification.verb],
            comment.get_permalink(),
            "comments/emails/notification.txt",
            "comments/emails/notification.html",
            {"comment": comment},
        )


def send_comment_deleted_email(comment: Comment):
    if comment.owner.has_email_pref(NOTIFICATION_PREFERENCES["delete"]):
        context = {"comment": comment}
        send_mail(
            NOTIFICATION_SUBJECTS["delete"],
            render_to_string("comments/emails/comment_deleted.txt", context),
            comment.community.resolve_email("no-reply"),
            [comment.owner.email],
            html_message=render_to_string(
                "comments/emails/comment_deleted.html", context
            ),
        )
