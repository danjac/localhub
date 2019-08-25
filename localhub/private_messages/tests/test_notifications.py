# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List

from localhub.private_messages.notifications import send_message_email
from localhub.private_messages.tests.factories import MessageFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestSendMessageEmail:
    def test_if_enabled(self, mailoutbox: List):
        user = UserFactory(email_preferences=["new_message"])
        message = MessageFactory(recipient=user)
        send_message_email(message)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [user.email]

    def test_if_disabled(self, mailoutbox: List):
        user = UserFactory(email_preferences=[])
        message = MessageFactory(recipient=user)
        send_message_email(message)
        assert len(mailoutbox) == 0
