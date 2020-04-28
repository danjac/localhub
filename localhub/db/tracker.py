# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class TrackerModelMixin:
    """Django Model Mixin allowing simple tracking of
    specific non-foreign key fields.

    Adds the following methods to the class:

    has_tracker_changed(*fields):

        returns True if any of the fields' values changed on the instance
        since the object was loaded from the database. If no fields are
        specified, then all tracked fields are checked.

    reset_tracker():

        resets the tracker to all the current values. Useful e.g. in testing.

    Example:

    class Comment(models.Model):
        content = models.TextField()
        tracked_fields = ["content"]
        ...

    comment = Comment(content="test")
    comment.has_tracker_changed() -> True: object not saved yet
    comment.save()

    comment = Comment.objects.get(pk=comment.id)
    comment.has_tracker_changed() -> False: retrieved object not changed
    comment.content = "test change!"
    comment.has_tracker_changed() -> True: retrieved value different from new value

    # comment.refresh_from_db() also has same effect...
    comment.reset_tracker()
    comment.has_tracker_changed() -> False
    """

    # would be nice to be able to do this in Meta...
    tracked_fields = []

    @classmethod
    def from_db(cls, db, field_names, values):
        new = super(TrackerModelMixin, cls).from_db(db, field_names, values)
        new._tracked_values = {
            field: values[field_names.index(field)] for field in cls.tracked_fields
        }

        return new

    def refresh_from_db(self, using=None, fields=None):
        super().refresh_from_db(using, fields)
        self.reset_tracker(fields)

    def reset_tracker(self, fields=None):
        """Reset tracker, so that fields will no longer be marked as changed.

        Args:
            fields (Iterable, optional): list of fields to reset. If None, then
                resets tracker on all tracked fields (default: None)
        """
        self._tracked_values = {
            field: getattr(self, field) for field in fields or self.tracked_fields
        }

    def has_tracker_changed(self, fields=None):
        """Checks if fields are dirty i.e. have changed since last DB load.

        Note that if this is called on an instance that has not yet been saved
        to the DB, this will always return True.

        Args:
            fields (Iterable, optional): list of fields to check. If None, checks
                all tracked fields (default: None).

        Returns:
            bool
        """
        if not hasattr(self, "_tracked_values"):
            return True
        for field in fields or self.tracked_fields:
            if getattr(self, field) != self._tracked_values[field]:
                return True
        return False
