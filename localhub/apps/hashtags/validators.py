# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

# Local
from .app_settings import HASHTAGS_RE


def validate_hashtags(value):
    """Ensure all tokens in value are valid hashtags.

    Args:
        value (str): a value. Can be empty.

    Raises:
        ValidationError
    """
    if not value:
        return

    for token in value.split():
        if not HASHTAGS_RE.match(token):
            raise ValidationError(_("All tokens must be valid #tags"))
