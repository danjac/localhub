# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from bfg.apps.notifications.factories import NotificationFactory
from bfg.apps.notifications.signals import notification_read

from ..factories import MessageFactory
from ..models import Message

pytestmark = pytest.mark.django_db


class TestMessageNotificationRead:
    def test_mark_read_when_notification_read(self):
        message = MessageFactory()
        NotificationFactory(content_object=message)
        notification_read.send(
            sender=Message, instance=message,
        )
        message.refresh_from_db()
        assert message.read
