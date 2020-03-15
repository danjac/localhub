# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override


def send_activity_deleted_email(activity):

    if activity.owner.send_email_notifications:
        with override(activity.owner.language):
            activity_name = activity._meta.verbose_name

            context = {"activity": activity, "activity_name": activity_name}

            send_mail(
                _("Your %s has been deleted by a moderator" % activity_name),
                render_to_string("activities/emails/activity_deleted.txt", context),
                activity.community.resolve_email("no-reply"),
                [activity.owner.email],
                html_message=render_to_string(
                    "activities/emails/activity_deleted.html", context
                ),
            )
