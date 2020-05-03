# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.db.models import DateTimeField, Func


class IntervalAdd(Func):
    """Base class for PostgreSQL interval arithmetic functions.
    """

    period = None
    arg_joiner = " + CAST("
    output_field = DateTimeField()

    @property
    def template(self):
        return "%(expressions)s || '" + self.period + "' AS INTERVAL)"


class DateAdd(IntervalAdd):
    period = "days"


class MonthAdd(IntervalAdd):
    period = "months"


class YearAdd(IntervalAdd):
    period = "years"
