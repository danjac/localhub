# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localhub.common.template.defaultfilters import from_dictkey


class TestFromDictkey:
    def test_is_dict(self):
        d = {"1": "3"}

        assert from_dictkey(d, "1") == "3"

    def test_is_none(self):
        assert from_dictkey(None, "1") is None
