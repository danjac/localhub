# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from localhub.activities.models import Activity
from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification


def send_activity_deleted_email(activity: Activity):
    activity_name = activity._meta.verbose_name

    context = {"activity": activity, "activity_name": activity_name}
    send_mail(
        _("Your %s has been deleted by a moderator" % activity_name),
        render_to_string("activities/emails/activity_deleted.txt", context),
        activity.community.resolve_email("notifications"),
        [activity.owner.email],
        html_message=render_to_string(
            "activities/emails/activity_deleted.html", context
        ),
    )


NOTIFICATION_SUBJECTS = {
    "created": _("Someone has published a new %s"),
    "flagged": _("Someone has flagged this %s"),
    "liked": _("Someone has liked your %s"),
    "mentioned": _("Someone has mentioned you in their %s"),
    "moderated": _("Someone has edited your %s"),
    "tagged": _("Someone has published a new %s you might be interested in"),
    "updated": _("Someone has updated their %s"),
}


def send_activity_notification_email(
    activity: Activity, notification: Notification
):

    activity_name = activity._meta.verbose_name

    send_notification_email(
        notification,
        NOTIFICATION_SUBJECTS[notification.verb] % activity_name,
        activity.get_permalink(),
        "activities/emails/notification.txt",
        "activities/emails/notification.html",
        {"activity_name": activity_name},
    )
