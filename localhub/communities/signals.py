# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from localhub.communities.models import Membership
from localhub.join_requests.models import JoinRequest


@receiver(
    post_delete, sender=Membership, dispatch_uid="memberships.membership_deleted",
)
def membership_deleted(instance, **kwargs):
    """
    Housekeeping: remove any join requests, so user can re-join.
    """

    def cleanup():
        JoinRequest.objects.filter(
            sender=instance.member, community=instance.community
        ).delete()

    transaction.on_commit(cleanup)
