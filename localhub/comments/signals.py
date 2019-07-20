# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.dispatch import receiver

from simple_history.signals import post_create_historical_record

from localhub.comments.emails import (
    send_comment_notification_email,
    send_comment_deleted_email,
)
from localhub.comments.models import Comment


@receiver(
    post_create_historical_record,
    sender=Comment.history.model,
    dispatch_uid="comments.create_historical_record",
)
def send_notifications(
    instance: Comment, history_instance: Comment.history.model, **kwargs
):
    def notify():
        if (
            history_instance.history_type == "-"
            and history_instance.history_user
            and history_instance.history_user != instance.owner
        ):
            send_comment_deleted_email(instance)
        else:
            for notification in instance.notify(
                history_instance.history_type == "+",
                history_instance.history_user,
            ):
                send_comment_notification_email(instance, notification)

    transaction.on_commit(notify)
