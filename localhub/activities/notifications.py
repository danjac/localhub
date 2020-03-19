# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _

from localhub.notifications.adapters import DefaultAdapter, Mailer, Webpusher
from localhub.users.utils import user_display

HEADERS = [
    ("delete", _("%(actor)s has deleted your %(object)s")),
    ("flag", _("%(actor)s has flagged this %(object)s")),
    ("like", _("%(actor)s has liked your %(object)s")),
    ("mention", _("%(actor)s has mentioned you in their %(object)s")),
    (
        "moderator_review",
        _("%(actor)s has submitted or updated their %(object)s for review"),
    ),
    ("followed_user", _("%(actor)s has submitted a new %(object)s")),
    (
        "followed_tag",
        _(
            "Someone has submitted or updated a new %(object)s containing tags you are following"  # noqa
        ),
    ),
    ("reshare", _("%(actor)s has reshared your %(object)s")),
]


class ActivityMailer(Mailer):
    HEADERS = HEADERS

    def get_subject(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": user_display(self.adapter.actor),
            "object": self.adapter.object_name,
        }

    def get_template_names(self, suffix):
        return super().get_template_names(suffix) + self.resolver.resolve(
            "activities/emails", suffix
        )


class ActivityWebpusher(Webpusher):
    HEADERS = HEADERS

    def get_header(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": user_display(self.adapter.actor),
            "object": self.adapter.object_name,
        }

    def get_body(self):
        return truncatechars(self.object.title, 60)


class ActivityAdapter(DefaultAdapter):

    ALLOWED_VERBS = [
        "delete",
        "flag",
        "like",
        "mention",
        "followed_user",
        "followed_tag",
        "reshare",
    ]

    mailer_class = ActivityMailer
    webpusher_class = ActivityWebpusher

    def get_template_names(self):
        return super().get_template_names() + self.resolver.resolve(
            "activities/includes"
        )
