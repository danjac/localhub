# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


from localhub.messageboard.models import Message, MessageRecipient


@receiver(
    post_save,
    sender=Message,
    dispatch_uid="messageboard.update_message_search_document",
)
def update_message_search_document(instance: Message, **kwargs):
    transaction.on_commit(lambda: instance.search_indexer.update())


@receiver(
    post_save,
    sender=MessageRecipient,
    dispatch_uid="messageboard.update_messagerecipient_search_document",
)
def update_messagerecipient_search_document(
    instance: MessageRecipient, **kwargs
):
    transaction.on_commit(lambda: instance.search_indexer.update())
