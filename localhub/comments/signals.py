# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


from localhub.comments.models import Comment


@receiver(
    post_save, sender=Comment, dispatch_uid="comments.update_search_document"
)
def update_search_document(instance, **kwargs):
    transaction.on_commit(lambda: instance.search_indexer.update())
