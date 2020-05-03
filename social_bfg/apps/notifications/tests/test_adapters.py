# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Social-BFG
from social_bfg.apps.posts.notifications import PostAdapter

from ..factories import NotificationFactory

pytestmark = pytest.mark.django_db


@pytest.fixture()
def adapter(notification):
    return PostAdapter(notification)


class TestAdapter:
    def test_is_allowed(self, adapter):
        assert adapter.is_allowed()

    def test_is_not_allowed(self):
        assert not PostAdapter(NotificationFactory(verb="not_allowed")).is_allowed()

    def test_render_to_tag(self, adapter):
        response = adapter.render_to_tag()
        assert "has mentioned you" in response
        assert "post" in response

    def test_send_notification(self, adapter, mailoutbox, send_webpush_mock):
        adapter.send_notification()
        assert send_webpush_mock.delay.called
        assert len(mailoutbox) == 1

    def test_webpusher_send(self, adapter, send_webpush_mock):
        adapter.webpusher.send()
        assert send_webpush_mock.delay.called

    def test_mailer_send(self, adapter, mailoutbox):
        adapter.mailer.send()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [adapter.notification.recipient.email]
