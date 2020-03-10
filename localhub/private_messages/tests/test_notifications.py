# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.users.factories import UserFactory

from ..factories import MessageFactory
from ..notifications import send_message_email

pytestmark = pytest.mark.django_db


class TestSendMessageEmail:
    def test_send_if_enabled(self, mailoutbox):
        user = UserFactory(send_email_notifications=True)
        message = MessageFactory(recipient=user)
        send_message_email(message)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [user.email]

    def test_send_if_disabled(self, mailoutbox):
        user = UserFactory(send_email_notifications=False)
        message = MessageFactory(recipient=user)
        send_message_email(message)
        assert len(mailoutbox) == 0
