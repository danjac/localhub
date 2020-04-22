# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class with_tracker:
    """Class decorator for models, allowing simple tracking of
    specific non-foreign key fields.

    NOTE: if with_tracker is used with a subclass, the parent class'
    tracked fields will NOT be inherited.

    Adds the following methods to the class:

    has_tracker_changed(*fields):

        returns True if any of the fields' values changed on the instance
        since the object was loaded from the database. If no fields are
        specified, then all tracked fields are checked.

    reset_tracker():

        resets the tracker to all the current values. Useful e.g. in testing.
    """

    def __init__(self, *tracked_fields):
        self.tracked_fields = tracked_fields

    def __call__(self, cls):
        def _reset(self_, fields=None):
            # reset tracked values to current values
            self_._tracked_values = {
                field: getattr(self_, field) for field in fields or self.tracked_fields
            }

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
            new._tracked_values = getattr(base, "_tracked_values", {})

            for field in self.tracked_fields:
                new._tracked_values[field] = values[field_names.index(field)]

            return new

        def _refresh_from_db(self_, using=None, fields=None):
            super(cls, self_).refresh_from_db(using, fields)
            self_.reset_tracker(fields)

        cls.from_db = classmethod(_from_db)
        cls.refresh_from_db = _refresh_from_db
        cls.has_tracker_changed = _has_changed
        cls.reset_tracker = _reset

        return cls
