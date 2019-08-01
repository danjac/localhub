# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional, Iterable, Type

from django.db.models import Model


class TrackerProxy:
    def __init__(self, model: Model, fields: Iterable[str], history_attr: str):

        self.model = model
        self.history_attr = history_attr
        self.fields = fields

    @property
    def first_record(self) -> Optional[Model]:
        return getattr(self.model, self.history_attr).first()

    @property
    def prev_record(self) -> Optional[Model]:
        return self.first_record.prev_record if self.first_record else None

    @property
    def changed_fields(self) -> List[str]:
        if self.first_record is None or self.prev_record is None:
            return []
        return self.first_record.diff_against(self.prev_record).changed_fields

    def changed(self, *fields) -> bool:
        return bool(
            set(self.changed_fields).intersection(set(fields or self.fields))
        )


class Tracker:
    """
    Uses simple_history HistoricalRecords to track if a set of fields
    have changed.
    """

    def __init__(self, fields: Iterable[str], history_attr: str = "history"):
        self.fields = fields
        self.history_attr = history_attr

    def __get__(self, instance: Model, owner: Type[Model]):
        return TrackerProxy(instance, self.fields, self.history_attr)
