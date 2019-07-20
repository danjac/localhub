# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction, models

from localhub.activities.emails import (
    send_activity_notification_email,
    send_activity_deleted_email,
)

from localhub.activities.models import Activity


def send_notifications(
    instance: Activity, history_instance: models.Model, **kwargs
):
    def notify():
        if (
            history_instance.history_type == "-"
            and history_instance.history_user
            and instance.owner != history_instance.history_user
        ):
            send_activity_deleted_email(instance)
        else:
            for notification in instance.notify(
                history_instance.history_type == "+",
                history_instance.history_user,
            ):
                send_activity_notification_email(instance, notification)

    transaction.on_commit(notify)
