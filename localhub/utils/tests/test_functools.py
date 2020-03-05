# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from ..functools import temp_attribute


class TestTempAttribute:
    def test_if_new_attr(self):
        class Thing:
            ...

        thing = Thing()
        with temp_attribute(thing, "size", 1):
            assert thing.size == 1
        assert not hasattr(thing, "size")

    def test_if_existing_attr(self):
        class Thing:
            size = 1

        thing = Thing()
        with temp_attribute(thing, "size", 2):
            assert thing.size == 2
        assert thing.size == 1
