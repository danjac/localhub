# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List

from localhub.messageboard.notifications import send_message_email
from localhub.messageboard.tests.factories import MessageRecipientFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestSendMessageEmail:
    def test_if_enabled(self, mailoutbox: List):
        user = UserFactory(email_preferences=["new_message"])
        recipient = MessageRecipientFactory(recipient=user)
        send_message_email(recipient)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [user.email]

    def test_if_disabled(self, mailoutbox: List):
        user = UserFactory(email_preferences=[])
        recipient = MessageRecipientFactory(recipient=user)
        send_message_email(recipient)
        assert len(mailoutbox) == 0
