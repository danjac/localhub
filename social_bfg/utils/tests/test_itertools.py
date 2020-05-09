# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Local
from ..itertools import takefirst


class TestTakefirst:
    def test_takefirst(self):
        notifications = [
            {"verb": "new_comment", "recipient": "a"},
            {"verb": "mention", "recipient": "b"},
            {"verb": "mention", "recipient": "a"},
        ]

        result = list(takefirst(notifications, lambda i: i["recipient"]))
        assert len(result) == 2
        assert result[0] == notifications[0]
        assert result[1] == notifications[1]
