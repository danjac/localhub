# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from localhub.communities.models import Community


def send_membership_deleted_email(
    member: settings.AUTH_USER_MODEL, community: Community
):
    context = {"member": member, "community": community}
    send_mail(
        _("Your membership of community %s has been deleted") % community,
        render_to_string("communities/emails/membership_deleted.txt", context),
        community.resolve_email("support"),
        [member.email],
        html_message=render_to_string(
            "communities/emails/membership_deleted.html", context
        ),
    )
