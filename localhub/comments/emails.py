# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils.translation import override

from localhub.comments.models import Comment
from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification


NOTIFICATION_SUBJECTS = {
    "flag": _("Someone has flagged this comment"),
    "like": _("Someone has liked your comment"),
    "mention": _("Someone has mentioned you in their comment"),
    "moderator_delete": _("Your comment has been deleted by a moderator"),
    "moderator_edit": _("A moderator has edited your comment"),
    "moderator_review_request": _(
        "Someone has posted or updated a comment to review"
    ),
    "new_comment": _("Someone has submitted a comment on one of your posts"),
    "new_sibling_comment": _(
        "Someone has made a comment on a post you've commented on"
    ),
    "new_followed_user_comment": _(
        "Someone you are following has submitted a new comment"
    ),
}


def send_comment_notification_email(
    comment: Comment, notification: Notification
):

    if notification.recipient.has_email_pref(notification.verb):
        with override(notification.recipient.language):
            plain_template_name = (
                f"comments/emails/notifications/{notification.verb}.txt"
            )
            html_template_name = (
                f"comments/emails/notifications/{notification.verb}.html"
            )

            send_notification_email(
                notification,
                NOTIFICATION_SUBJECTS[notification.verb],
                comment.get_permalink(),
                plain_template_name,
                html_template_name,
                {"comment": comment},
            )


def send_comment_deleted_email(comment: Comment):
    if comment.owner.has_email_pref("moderator_delete"):
        with override(comment.owner.language):
            context = {"comment": comment}
            send_mail(
                NOTIFICATION_SUBJECTS["moderator_delete"],
                render_to_string(
                    "comments/emails/comment_deleted.txt", context
                ),
                comment.community.resolve_email("no-reply"),
                [comment.owner.email],
                html_message=render_to_string(
                    "comments/emails/comment_deleted.html", context
                ),
            )
