# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from localhub.activities.models import Activity
from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification


def send_activity_deleted_email(activity: Activity):

    if activity.owner.has_email_pref("moderator_delete"):
        activity_name = activity._meta.verbose_name

        context = {"activity": activity, "activity_name": activity_name}
        send_mail(
            _("Your %s has been deleted by a moderator" % activity_name),
            render_to_string(
                "activities/emails/activity_deleted.txt", context
            ),
            activity.community.resolve_email("no-reply"),
            [activity.owner.email],
            html_message=render_to_string(
                "activities/emails/activity_deleted.html", context
            ),
        )


NOTIFICATION_SUBJECTS = {
    "flag": _("Someone has flagged this %s"),
    "like": _("Someone has liked your %s"),
    "mention": _("Someone has mentioned you in their %s"),
    "moderator_edit": _("A moderator has edited your %s"),
    "moderator_review_request": _("Someone has created a new %s to review"),
    "new_followed_user_post": _(
        "Someone you are following has created a new %s"
    ),
    "new_followed_user_tag": _(
        "Someone has created a new %s containing tags you are following"
    ),
    "reshare": _("Someone has reshared your %s"),
}


def send_activity_notification_email(
    activity: Activity, notification: Notification
):

    if notification.recipient.has_email_pref(notification.verb):
        activity_name = activity._meta.verbose_name

        send_notification_email(
            notification,
            NOTIFICATION_SUBJECTS[notification.verb] % activity_name,
            activity.get_permalink(),
            "activities/emails/notification.txt",
            "activities/emails/notification.html",
            {"activity_name": activity_name},
        )
