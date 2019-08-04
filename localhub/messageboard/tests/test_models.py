# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.messageboard.models import Message, MessageRecipient
from localhub.messageboard.tests.factories import (
    MessageFactory,
    MessageRecipientFactory,
)

pytestmark = pytest.mark.django_db


class TestMessageManager:
    def test_search(self):
        message = MessageFactory(subject="testme")
        message.search_indexer.update()
        assert Message.objects.search("testme").get() == message


class TestMessageRecipientManager:
    def test_search(self):
        message = MessageFactory(subject="testme")
        recipient = MessageRecipientFactory(message=message)
        message.search_indexer.update()
        assert MessageRecipient.objects.search("testme").get() == recipient
