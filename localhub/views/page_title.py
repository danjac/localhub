# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.encoding import smart_text


class PageTitleMixin:
    """
    Applies subtitle to <title> tags
    """

    page_title_segments = []
    page_title_divider = " / "

    @property
    def page_title(self):
        return self.page_title_divider.join(
            [str(s) for s in self.get_page_title_segments()]
        )

    def get_page_title_segments(self):
        return self.page_title_segments
