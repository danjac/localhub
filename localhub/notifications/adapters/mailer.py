# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail

from .template import TemplateRenderer


class Mailer:
    """
    Manages Notification plain and HTML emails.
    """

    renderer_class = TemplateRenderer
    sender_address = "no-reply"

    def __init__(self, adapter):
        self.adapter = adapter
        self.renderer = self.renderer_class(self.adapter, self.get_template_prefixes())

    def send(self, **kwargs):
        recipient = self.get_recipient()

        if recipient.send_email_notifications:
            subject = self.get_subject()
            context = {"subject": subject}

            return send_mail(
                f"{self.adapter.community.name} | {subject}",
                self.renderer.render(suffix=(".txt"), extra_context=context),
                self.get_sender(),
                [recipient.email],
                html_message=self.renderer.render(
                    suffix=".html", extra_context=context
                ),
                **kwargs,
            )

    def get_subject(self):
        return str(self.adapter.object)

    def get_sender(self):
        return self.adapter.community.resolve_email(self.sender_address)

    def get_recipient(self):
        return self.adapter.recipient

    def get_template_prefixes(self):
        return [f"{self.adapter.app_label}/emails"]
