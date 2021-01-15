# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404
from django.utils.translation import gettext as _


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


def paginate(
    request,
    queryset,
    page_size=settings.DEFAULT_PAGE_SIZE,
    param="page",
    allow_empty=True,
    orphans=0,
    paginator_class=PresetCountPaginator,
):

    paginator = Paginator(
        queryset, page_size, allow_empty_first_page=allow_empty, orphans=orphans
    )
    try:
        return paginator.page(int(request.GET.get(param, 1)))
    except (ValueError, InvalidPage):
        raise Http404(_("Invalid page"))
