# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext as _, override

from localhub.join_requests.models import JoinRequest


def send_join_request_email(join_request: JoinRequest):
    context = {
        "join_request": join_request,
        "list_url": join_request.community.resolve_url(
            reverse("join_requests:list")
        ),
    }

    for admin in join_request.community.get_admins():
        with override(admin.language):

            send_mail(
                _("%s | Someone has requested to join this community")
                % join_request.community.name,
                render_to_string(
                    "join_requests/emails/join_request.txt", context
                ),
                join_request.community.resolve_email("no-reply"),
                [admin.email],
                html_message=render_to_string(
                    "join_requests/emails/join_request.html", context
                ),
            )


def send_acceptance_email(join_request: JoinRequest):
    sender = join_request.get_sender()
    with override(sender.language if sender else settings.LANGUAGE_CODE):
        context = {"join_request": join_request, "user": sender}
        send_mail(
            _("Your request has been approved"),
            render_to_string("join_requests/emails/accepted.txt", context),
            join_request.community.resolve_email("no-reply"),
            [join_request.sender.email],
            html_message=render_to_string(
                "join_requests/emails/accepted.html", context
            ),
        )


def send_rejection_email(join_request: JoinRequest):
    sender = join_request.get_sender()
    with override(sender.language if sender else settings.LANGUAGE_CODE):
        context = {"join_request": join_request}
        send_mail(
            _("Your request has been rejected"),
            render_to_string("join_requests/emails/rejected.txt", context),
            join_request.community.resolve_email("no-reply"),
            [sender.email if sender else join_request.email],
            html_message=render_to_string(
                "join_requests/emails/rejected.html", context
            ),
        )
