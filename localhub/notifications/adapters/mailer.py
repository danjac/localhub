# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail


class Mailer:
    """
    Manages Notification plain and HTML emails.
    """

    def __init__(self, adapter):

        self.adapter = adapter
        self.renderer = adapter.renderer

        self.object = self.adapter.object
        self.community = self.adapter.community
        self.recipient = self.adapter.recipient
        self.app_label = self.adapter.app_label

    def render(self, **template_kwargs):
        return self.renderer.render(
            prefix=f"{self.app_label}/emails", **template_kwargs
        )

    def send(self, **email_kwargs):
        if self.recipient.send_email_notifications:
            subject = self.get_subject()
            context = {"subject": subject}

            return send_mail(
                f"{self.community.name} | {subject}",
                self.render(suffix=".txt", extra_context=context),
                self.get_sender(),
                [self.recipient.email],
                html_message=self.render(suffix=".html", extra_context=context),
                **email_kwargs,
            )

    def get_subject(self):
        return str(self.object)

    def get_sender(self):
        return self.community.resolve_email("no-reply")
