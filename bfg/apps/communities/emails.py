# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils.translation import override


def send_membership_deleted_email(member, community):
    with override(member.language):
        context = {"member": member, "community": community}
        send_mail(
            _("Your membership of community %(community)s has been terminated")
            % {"community": community.name},
            render_to_string("communities/emails/membership_deleted.txt", context),
            community.resolve_email("support"),
            [member.email],
            html_message=render_to_string(
                "communities/emails/membership_deleted.html", context
            ),
        )
