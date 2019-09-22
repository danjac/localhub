# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer

from localhub.private_messages.models import Message


# @receiver(
# post_save,
# sender=Message,
# dispatch_uid="private_messages.send_message_to_channel",
# )
def send_message_to_channel(instance, created, **kwargs):
    if not created:
        return

    def do_send():
        payload = {
            "type": "message",
            "key": "message",
            "message_id": str(instance.id),
            "community": instance.community,
            "sender": instance.sender,
            "recipient": instance.recipient,
        }
        async_to_sync(get_channel_layer().group_send)(
            instance.recipient.username, payload
        )

    transaction.on_commit(do_send)
