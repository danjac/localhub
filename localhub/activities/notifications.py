# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from localhub.notifications.emails import send_notification_email
from localhub.notifications.utils import send_push_notification
from localhub.users.utils import user_display

NOTIFICATION_HEADERS = {
    "flag": _("%(actor)s has flagged this %(activity)s"),
    "like": _("%(actor)s has liked your %(activity)s"),
    "mention": _("%(actor)s has mentioned you in their %(activity)s"),
    "moderator_edit": _("A moderator has edited your %(activity)s"),
    "moderator_review_request": _(
        "%(actor)s has submitted or updated their %(activity)s for review"
    ),
    "new_followed_user_post": _("%(actor)s has submitted a new %(activity)s"),
    "new_followed_tag_post": _(
        "Someone has submitted or updated a new %(activity)s containing tags you are following" # noqa
    ),
    "reshare": _("%(actor)s has reshared your %(activity)s"),
}


def send_activity_notifications(activity, notification):
    send_activity_notification_push(activity, notification)
    send_activity_notification_email(activity, notification)


def send_activity_notification_push(activity, notification):
    with override(notification.recipient.language):

        send_push_notification(
            notification.recipient,
            notification.community,
            head=get_notification_header(activity, notification),
            body=force_text(activity),
            url=activity.get_permalink(),
        )


def send_activity_notification_email(activity, notification):
    with override(notification.recipient.language):
        activity_name = activity._meta.verbose_name

        plain_template_name = f"activities/emails/notifications/{notification.verb}.txt"
        html_template_name = f"activities/emails/notifications/{notification.verb}.html"

        send_notification_email(
            notification,
            get_notification_header(activity, notification),
            activity.get_permalink(),
            plain_template_name,
            html_template_name,
            {"activity_name": activity_name},
        )


def get_notification_header(activity, notification):
    return NOTIFICATION_HEADERS[notification.verb] % {
        "actor": user_display(notification.actor),
        "activity": activity._meta.verbose_name,
    }


def send_activity_deleted_email(activity):

    if activity.owner.has_notification_pref("moderator_delete"):
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
