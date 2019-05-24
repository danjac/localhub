# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from communikit.posts.models import PostNotification


def send_notification_email(notification: PostNotification):
    subject = {
        "mentioned": _("You have been mentioned in a post"),
        "created": _("A user has published a post to the %s community")
        % notification.post.community.name,
        "updated": _("A user has edited their post in the %s community")
        % notification.post.community.name,
    }[notification.verb]
    send_mail(
        subject,
        render_to_string(
            "posts/emails/notification.txt",
            {
                "notification": notification,
                "post_url": notification.post.get_permalink(),
                # "owner_url": notification.post.owner.get_permalink(
                # notification.post.community
                # ),
            },
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{notification.post.community.domain}",
        [notification.recipient.email],
    )
