# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.notifications.adapter import BaseNotificationAdapter
from localhub.users.utils import user_display


class ActivityNotificationAdapter(BaseNotificationAdapter):
    NOTIFICATION_HEADERS = [
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

    def get_notification_header(self):
        return dict(self.NOTIFICATION_HEADERS)[self.verb] % {
            "actor": user_display(self.actor),
            "object": self.object_name,
        }

    def get_email_subject(self):
        return self.get_notification_header()

    def get_webpush_header(self):
        return self.get_notification_header()

    def get_template_names(self):
        return super().get_template_names() + self.resolve_template_names(
            f"activities/includes"
        )

    def get_plain_email_template_names(self):
        return super().get_plain_email_template_names() + self.resolve_template_names(
            f"activities/emails", ".txt"
        )

    def get_html_email_template_names(self):
        return super().get_html_email_template_names() + self.resolve_template_names(
            f"activities/emails",
        )
