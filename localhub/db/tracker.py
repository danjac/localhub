# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class with_tracker:
    def __init__(self, *tracked_fields):
        self.tracked_fields = tracked_fields

    def __call__(self, cls):
        def _has_changed(self_, *fields):
            # if "tracked_fields" attribute is not set, then it
            # hasn't been loaded from DB yet, hence is new...
            if not hasattr(self_, "_tracked_values"):
                return True
            for field in fields or self.tracked_fields:
                if getattr(self_, field) != self_._tracked_values[field]:
                    return True
            return False

        def _from_db(base, db, field_names, values):
            new = super(cls, base).from_db(db, field_names, values)
            new._tracked_values = {}

            for field in self.tracked_fields:
                new._tracked_values[field] = values[field_names.index(field)]

            return new

        cls.from_db = classmethod(_from_db)
        cls.has_tracker_changed = _has_changed

        return cls
