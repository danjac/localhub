from django.core.mail import send_mail
from django.template import loader
from django.urls import reverse
from django.utils.translation import ugettext as _

from communikit.invites.models import Invite


def send_invitation_email(invite: Invite):
    # tbd: we'll use django-templated-mail at some point
    send_mail(
        _("Invitation to join"),
        loader.get_template("invites/emails/invitation.txt").render(
            {
                "invite": invite,
                "accept_url": invite.community.domain_url(
                    reverse("invites:accept", args=[invite.id])
                ),
            }
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{invite.community.domain}",
        [invite.email],
    )
