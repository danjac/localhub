# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from ..text import slugify_unicode


class TestSlugifyUnicode:
    def test_slugify_unicode_if_plain_ascii(self):
        assert slugify_unicode("test") == "test"

    def test_slugify_unicode_if_unicode(self):
        assert slugify_unicode("Байконур") == "baikonur"
