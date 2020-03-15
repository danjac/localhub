# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override


def send_comment_deleted_email(comment):
    if comment.owner.send_email_notifications:
        with override(comment.owner.language):
            context = {"comment": comment}
            send_mail(
                _("A moderator has deleted your comment"),
                render_to_string("comments/emails/comment_deleted.txt", context),
                comment.community.resolve_email("no-reply"),
                [comment.owner.email],
                html_message=render_to_string(
                    "comments/emails/comment_deleted.html", context
                ),
            )
