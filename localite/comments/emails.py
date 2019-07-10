# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from localite.comments.models import Comment


def send_deletion_email(comment: Comment):
    send_mail(
        _("Your comment has been deleted by a moderator"),
        render_to_string("comments/emails/deletion.txt", {"comment": comment}),
        comment.community.resolve_email("notifications"),
        [comment.owner.email],
    )
