# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils.translation import gettext_lazy as _

# Localhub
from localhub.apps.notifications.adapter import Adapter, Mailer, Webpusher
from localhub.apps.notifications.decorators import register

# Local
from .models import Comment


class CommentHeadersMixin:
    HEADERS = [
        ("delete", _("%(actor)s has deleted this comment")),
        ("flag", _("%(actor)s has flagged this comment")),
        ("like", _("%(actor)s has liked your comment")),
        ("mention", _("%(actor)s has mentioned you in their comment")),
        (
            "moderator_review",
            _("%(actor)s has submitted or updated a comment for review"),
        ),
        ("new_comment", _("%(actor)s has submitted a comment on one of your posts")),
        (
            "new_sibling",
            _("%(actor)s has made a comment on a post you've commented on"),
        ),
        ("reply", _("%(actor)s has replied to your comment")),
        ("followed_user", _("%(actor)s has submitted a new comment")),
    ]


class CommentMailer(CommentHeadersMixin, Mailer):
    def get_subject(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": self.adapter.actor.get_display_name()
        }


class CommentWebpusher(CommentHeadersMixin, Webpusher):
    def get_header(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": self.adapter.actor.get_display_name()
        }

    def get_body(self):
        return self.adapter.object.abbreviate()


@register(Comment)
class CommentAdapter(Adapter):
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
