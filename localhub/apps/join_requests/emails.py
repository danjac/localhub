# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.translation import override


def send_join_request_email(join_request):
    context = {
        "join_request": join_request,
        "detail_url": join_request.community.resolve_url(
            join_request.get_absolute_url()
        ),
        "list_url": join_request.community.resolve_url(reverse("join_requests:list")),
    }

    for admin in join_request.community.get_admins().filter(
        send_email_notifications=True
    ):
        with override(admin.language):

            send_mail(
                _("%s | Someone has requested to join this community")
                % join_request.community.name,
                render_to_string("join_requests/emails/join_request.txt", context),
                join_request.community.resolve_email("no-reply"),
                [admin.email],
                html_message=render_to_string(
                    "join_requests/emails/join_request.html", context
                ),
            )


def send_acceptance_email(join_request):
    send_email_to_sender(
        join_request,
        _("Your request has been accepted"),
        "join_requests/emails/accepted.txt",
        "join_requests/emails/accepted.html",
    )


def send_rejection_email(join_request):
    send_email_to_sender(
        join_request,
        _("Your request has been rejected"),
        "join_requests/emails/rejected.txt",
        "join_requests/emails/rejected.html",
    )


def send_email_to_sender(join_request, subject, plain_template, html_template):
    with override(join_request.sender.language):
        context = {"join_request": join_request, "user": join_request.sender}
        send_mail(
            subject,
            render_to_string(plain_template, context),
            join_request.community.resolve_email("no-reply"),
            [join_request.sender.email],
            html_message=render_to_string(html_template, context),
        )
