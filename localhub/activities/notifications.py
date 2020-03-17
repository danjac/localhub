# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.notifications import (
    BaseNotificationAdapter,
    Mailer,
    TemplateResolver,
    Webpusher,
)
from localhub.users.utils import user_display

HEADERS = [
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


class ActivityTemplateResolver(TemplateResolver):
    def resolve(self, prefix, suffix=".html"):
        return super().resolve(prefix, suffix) + super().resolve(
            "activities/includes", suffix
        )


class ActivityEmailTemplateResolver(TemplateResolver):
    def resolve(self, prefix, suffix=".html"):
        return super().resolve(prefix, suffix) + super().resolve(
            "activities/emails", suffix
        )


class ActivityMailer(Mailer):
    def get_subject(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": user_display(self.adapter.actor)
        }


class ActivityWebpusher(Webpusher):
    HEADERS = HEADERS

    def get_header(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": user_display(self.adapter.actor)
        }


class ActivityNotificationAdapter(BaseNotificationAdapter):

    mailer_class = ActivityMailer
    webpusher_class = ActivityWebpusher
    resolver_class = ActivityTemplateResolver
    email_resolver_class = ActivityEmailTemplateResolver
