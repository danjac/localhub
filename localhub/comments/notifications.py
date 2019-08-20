# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from localhub.comments.models import Comment
from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification
from localhub.notifications.utils import send_push_notification

NOTIFICATION_HEADERS = {
    "flag": _("%(actor)s has flagged this comment"),
    "like": _("%(actor)s has liked your comment"),
    "mention": _("%(actor)s has mentioned you in their comment"),
    "moderator_delete": _("A moderator has deleted your comment"),
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


def send_comment_notifications(comment: Comment, notification: Notification):
    send_comment_notification_push(comment, notification)
    send_comment_notification_email(comment, notification)


def get_notification_header(notification: Notification) -> str:
    return (
        NOTIFICATION_HEADERS[notification.verb]
        % {"actor": notification.actor},
    )


def send_comment_notification_push(
    comment: Comment, notification: Notification
):
    with override(notification.recipient.language):

        send_push_notification(
            notification.recipient,
            notification.community,
            head=get_notification_header(notification),
            body=force_text(truncatechars(comment.content, 60)),
            url=comment.get_permalink(),
        )


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
                get_notification_header(notification),
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
                NOTIFICATION_HEADERS["moderator_delete"],
                render_to_string(
                    "comments/emails/comment_deleted.txt", context
                ),
                comment.community.resolve_email("no-reply"),
                [comment.owner.email],
                html_message=render_to_string(
                    "comments/emails/comment_deleted.html", context
                ),
            )
