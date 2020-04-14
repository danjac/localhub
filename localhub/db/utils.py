# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.db import models


def boolean_value(value):
    """Returns a static boolean value for queryset annotation.

    Args:
        value (bool)

    Returns:
        Value
    """
    return models.Value(value, output_field=models.BooleanField())
