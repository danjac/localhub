# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


from localhub.users.models import User


@receiver(post_save, sender=User, dispatch_uid="users.update_search_document")
def update_search_document(instance: User, **kwargs):
    transaction.on_commit(lambda: instance.search_indexer.update())
