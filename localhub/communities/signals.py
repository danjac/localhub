# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Localhub
from localhub.join_requests.models import JoinRequest

# Local
from .models import Membership


@receiver(
    post_delete, sender=Membership, dispatch_uid="memberships.membership_deleted",
)
def membership_deleted(instance, **kwargs):
    """
    Housekeeping: remove any join requests, so user can re-join.
    """

    def cleanup():
        try:
            JoinRequest.objects.filter(
                sender=instance.member, community=instance.community
            ).delete()
        except ObjectDoesNotExist:
            pass

    transaction.on_commit(cleanup)
