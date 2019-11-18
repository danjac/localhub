# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.paginator import Paginator


class PresetCountPaginator(Paginator):
    """
    Paginator which presets the total count, so you can have a separately
    calculated query in situations where using naive object_list.count()
    will be expensive and you need something more fine-tuned and efficient.

    This is particularly useful with UNION querysets which will include
    all annotations across multiple sub-querysets.
    """

    def __init__(self, count, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preset_count = count

    @property
    def count(self):
        return self._preset_count
