# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from localhub.polls.models import Poll


@receiver(post_save, sender=Poll, dispatch_uid="polls.taggit")
def taggit(instance, created, **kwargs):
    transaction.on_commit(lambda: instance.taggit(created))
