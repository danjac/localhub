# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils.encoding import smart_text
from django.utils.text import slugify

# Third Party Libraries
from unidecode import unidecode


def slugify_unicode(text):
    """
    Slugify to ASCII attempting to render any Unicode text.
    """
    return slugify(unidecode(smart_text(text)), allow_unicode=False)
