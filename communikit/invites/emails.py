# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext as _

from communikit.invites.models import Invite


def send_invitation_email(invite: Invite):
    send_mail(
        _("Invitation to join"),
        render_to_string(
            "invites/emails/invitation.txt",
            {
                "invite": invite,
                "accept_url": invite.community.domain_url(
                    reverse("invites:accept", args=[invite.id])
                ),
            },
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{invite.community.domain}",
        [invite.email],
    )
