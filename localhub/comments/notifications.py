# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.notifications.adapters import DefaultAdapter, Mailer, Webpusher
from localhub.notifications.decorators import register
from localhub.users.utils import user_display

from .models import Comment

HEADERS = [
    ("delete", _("%(actor)s has deleted this comment")),
    ("flag", _("%(actor)s has flagged this comment")),
    ("like", _("%(actor)s has liked your comment")),
    ("mention", _("%(actor)s has mentioned you in their comment")),
    ("moderator_review", _("%(actor)s has submitted or updated a comment to review")),
    ("new_comment", _("%(actor)s has submitted a comment on one of your posts")),
    ("new_sibling", _("%(actor)s has made a comment on a post you've commented on")),
    ("reply", _("%(actor)s has replied to your comment")),
    ("followed_user", _("%(actor)s has submitted a new comment")),
]


class CommentMailer(Mailer):
    def get_subject(self):
        return dict(HEADERS)[self.adapter.verb] % {
            "actor": user_display(self.adapter.actor)
        }


class CommentWebpusher(Webpusher):
    def get_header(self):
        return dict(HEADERS)[self.adapter.verb] % {
            "actor": user_display(self.adapter.actor)
        }

    def get_body(self):
        return self.object.abbreviate()


@register(Comment)
class CommentAdapter(DefaultAdapter):
    ALLOWED_VERBS = [
        "delete",
        "flag",
        "followed_user",
        "like",
        "mention",
        "new_comment",
        "new_sibling",
        "reply",
    ]

    mailer_class = CommentMailer
    webpusher_class = CommentWebpusher
