# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _

from localhub.invites.models import Invite


def send_invitation_email(invite: Invite):
    send_mail(
        _("Invitation to join"),
        render_to_string(
            "invites/emails/invitation.txt",
            {
                "invite": invite,
                "accept_url": invite.community.resolve_url(
                    reverse("invites:accept", args=[invite.id])
                ),
            },
        ),
        invite.community.resolve_email("invites"),
        [invite.email],
    )
