# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from communikit.comments.models import CommentNotification


def send_notification_email(notification: CommentNotification):
    subject = {
        "mentioned": _("You have been mentioned in a comment"),
        "commented": _("A user has commented on your content"),
        "created": _("A user has posted a comment to the %s community")
        % notification.comment.activity.community.name,
        "updated": _("A user has updated their comment in the %s community")
        % notification.comment.activity.community.name,
    }[notification.verb]
    send_mail(
        subject,
        render_to_string(
            "comments/emails/notification.txt",
            {
                "notification": notification,
                "comment_url": notification.comment.get_permalink(),
                # "owner_url": notification.post.owner.get_permalink(
                # notification.post.community
                # ),
            },
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{notification.comment.activity.community.domain}",
        [notification.recipient.email],
    )
