# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from ..forms import PostForm


class TestPostForm:
    def test_url_missing(self):

        form = PostForm({"title": "something", "url": "", "description": "test"})

        assert form.is_valid()

    def test_title_missing(self):

        form = PostForm({"title": "", "url": "http://google.com"})

        assert form.is_valid()

    def test_title_and_url_both_missing(self):

        form = PostForm({"title": "", "url": "", "description": ""})

        assert not form.is_valid()
