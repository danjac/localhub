# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class Tracker:
    """
    Uses simple_history HistoricalRecords to track if a set of fields
    have changed.
    """

    def __init__(self, fields, history_attr="history"):
        self.fields = fields
        self.history_attr = history_attr

    def __get__(self, instance, owner):
        return InstanceTracker(instance, self.fields, self.history_attr)


class InstanceTracker:
    def __init__(self, instance, fields, history_attr):

        self.instance = instance
        self.fields = fields
        self.history_attr = history_attr

    @property
    def first_record(self):
        return getattr(self.instance, self.history_attr).first()

    @property
    def prev_record(self):
        return self.first_record.prev_record if self.first_record else None

    @property
    def changed_fields(self):
        if self.first_record is None or self.prev_record is None:
            return []
        return self.first_record.diff_against(self.prev_record).changed_fields

    def changed(self, *fields):
        return bool(
            set(self.changed_fields).intersection(set(fields or self.fields))
        )
