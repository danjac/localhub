# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail

from .template import TemplateContext, TemplateRenderer, TemplateResolver


class Mailer:
    """
    Manages Notification plain and HTML emails.
    """

    resolver_class = TemplateResolver
    renderer_class = TemplateRenderer
    context_class = TemplateContext

    def __init__(self, adapter):
        self.adapter = adapter

        self.object = self.adapter.object
        self.community = self.adapter.community
        self.recipient = self.adapter.recipient
        self.app_label = self.adapter.app_label

        self.renderer = self.renderer_class()
        self.resolver = self.resolver_class(self.adapter)
        self.context = self.context_class(self.adapter)

    def get_template_names(self, suffix):
        return self.resolver.resolve(f"{self.app_label}/emails", suffix)

    def send(self, **kwargs):
        if self.recipient.send_email_notifications:
            subject = self.get_subject()
            context = self.context.get_context({"subject": subject})

            return send_mail(
                f"{self.community.name} | {subject}",
                self.renderer.render(self.get_template_names(".txt"), context),
                self.get_sender(),
                [self.recipient.email],
                html_message=self.renderer.render(
                    self.get_template_names(".html"), context
                ),
                **kwargs,
            )

    def get_subject(self):
        return str(self.object)

    def get_sender(self):
        return self.community.resolve_email("no-reply")
