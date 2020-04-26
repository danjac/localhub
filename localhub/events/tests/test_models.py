# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.encoding import force_str

import pytest
import pytz

from localhub.communities.factories import MembershipFactory
from localhub.users.factories import UserFactory

from ..factories import EventFactory
from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventManager:
    def test_for_month_if_invalid_date(self):
        with pytest.raises(Event.InvalidDate):
            Event.objects.for_month(month=13, year=2020)

    def test_for_month(self,):
        """Should fall into range.
        """
        now = timezone.now()
        EventFactory(starts=now)
        qs = Event.objects.for_month(month=now.month, year=now.year)
        assert qs.count() == 1

    def test_for_date_if_invalid_date(self):
        with pytest.raises(Event.InvalidDate):
            Event.objects.for_date(day=33, month=13, year=2020)

    def test_for_date(self,):
        """Should match date.
        """
        now = timezone.now()
        EventFactory(starts=now)
        qs = Event.objects.for_date(day=now.day, month=now.month, year=now.year,)
        assert qs.count() == 1

    def test_for_dates_if_non_repeating_event_matches(self):
        """For a specific date, returns if start date matches this date.
        """
        now = timezone.now()
        EventFactory(starts=now)
        qs = Event.objects.for_dates(now)
        assert qs.count() == 1

    def test_for_dates_if_non_repeating_event_and_within_date_range_matches(self,):
        """Should fall into range
        """
        now = timezone.now()
        EventFactory(starts=now)
        qs = Event.objects.for_dates(now - timedelta(days=3), now + timedelta(days=3),)
        assert qs.count() == 1

    def test_for_dates_if_non_repeating_event_not_matches(self):
        """For a specific date, returns if start date matches this date.
        """
        now = timezone.now()
        EventFactory(starts=now - timedelta(days=30))
        qs = Event.objects.for_dates(now)
        assert qs.count() == 0

    def test_for_dates_if_non_repeating_event_and_within_date_range_not_matches(self,):
        """Should fall into range
        """
        now = timezone.now()
        EventFactory(starts=now - timedelta(days=30))
        qs = Event.objects.for_dates(now - timedelta(days=3), now + timedelta(days=3),)
        assert qs.count() == 0

    def test_for_dates_if_non_repeating_range_and_start_date_is_first_date(self):
        """Should be inclusive
        """
        date_from = timezone.now()
        date_to = date_from + timedelta(days=30)

        EventFactory(starts=date_from, repeats=None)
        qs = Event.objects.for_dates(date_from, date_to)
        assert qs.count() == 1

    def test_for_dates_if_non_repeating_range_and_start_date_is_last_date(self):
        """Should be inclusive
        """
        date_from = timezone.now()
        date_to = date_from + timedelta(days=30)

        EventFactory(starts=date_to, repeats=None)
        qs = Event.objects.for_dates(date_from, date_to)
        assert qs.count() == 1

    def test_for_dates_if_repeating_range_and_start_date_is_first_date(self):
        """Should be inclusive
        """
        date_from = timezone.now()
        date_to = date_from + timedelta(days=30)

        EventFactory(
            starts=date_from, repeats=Event.RepeatChoices.WEEKLY,
        )
        qs = Event.objects.for_dates(date_from, date_to)
        assert qs.count() == 1

    def test_for_dates_if_repeating_range_and_start_date_is_last_date(self):
        """Should be inclusive
        """
        date_from = timezone.now()
        date_to = date_from + timedelta(days=30)

        EventFactory(
            starts=date_to, repeats=Event.RepeatChoices.WEEKLY,
        )
        qs = Event.objects.for_dates(date_from, date_to)
        assert qs.count() == 1

    def test_for_dates_if_repeating_and_start_date_in_past(self):
        """If repeating, then OK if start date any time before today
        """
        now = timezone.now()
        EventFactory(
            starts=now - timedelta(days=30), repeats=Event.RepeatChoices.WEEKLY,
        )
        qs = Event.objects.for_dates(now)
        assert qs.count() == 1

    def test_for_dates_if_repeating_and_start_date_in_future(self):
        """Ignore if repeating and not started yet.
        """
        now = timezone.now()
        EventFactory(
            starts=now + timedelta(days=30), repeats=Event.RepeatChoices.WEEKLY,
        )
        qs = Event.objects.for_dates(now)
        assert qs.count() == 0

    def test_for_dates_if_repeating_and_start_date_in_range(self):
        """Should be ok if start date within range
        """
        now = timezone.now()
        EventFactory(
            starts=now + timedelta(days=3), repeats=Event.RepeatChoices.WEEKLY,
        )
        qs = Event.objects.for_dates(now - timedelta(days=3), now + timedelta(days=7),)
        assert qs.count() == 1

    def test_for_dates_if_repeating_and_start_date_outside_of_range(self):
        """Should be ok if start date within range
        """
        now = timezone.now()
        EventFactory(
            starts=now + timedelta(days=30), repeats=Event.RepeatChoices.WEEKLY,
        )
        qs = Event.objects.for_dates(now - timedelta(days=3), now + timedelta(days=7),)
        assert qs.count() == 0

    def test_next_date_if_not_repeats(self):
        "Should be same as start date if no repeat specified"
        event = EventFactory(repeats=None)
        first = Event.objects.with_next_date().first()
        assert first.next_date == event.starts

    def test_next_date_if_repeats_daily_before_start_date(self):
        "Should be same as start date if no repeat specified"
        event = EventFactory(
            repeats=Event.RepeatChoices.DAILY,
            starts=timezone.now() + timedelta(days=14),
        )
        first = Event.objects.with_next_date().first()
        assert first.next_date == event.starts

    def test_next_date_if_repeats_daily_after_start_date(self):
        now = timezone.now()
        EventFactory(repeats=Event.RepeatChoices.DAILY, starts=now - timedelta(days=14))
        first = Event.objects.with_next_date().first()
        assert (first.next_date.date() - datetime.date.today()).days == 1

    def test_next_date_if_repeats_weekly_before_start_date(self):
        "Should be same as start date if no repeat specified"
        event = EventFactory(
            repeats=Event.RepeatChoices.WEEKLY,
            starts=timezone.now() + timedelta(days=14),
        )
        first = Event.objects.with_next_date().first()
        assert first.next_date == event.starts

    def test_next_date_if_repeats_weekly_after_start_date(self):
        now = timezone.now()
        event = EventFactory(
            repeats=Event.RepeatChoices.WEEKLY, starts=now - timedelta(days=14)
        )
        first = Event.objects.with_next_date().first()
        assert first.next_date.weekday() == event.starts.weekday()
        assert ((first.next_date.date() - datetime.date.today()).days) % 7 == 0

    def test_next_date_if_repeats_monthly_before_start_date(self):
        "Should be same as start date if no repeat specified"
        event = EventFactory(
            repeats=Event.RepeatChoices.MONTHLY,
            starts=timezone.now() + timedelta(days=14),
        )
        first = Event.objects.with_next_date().first()
        assert first.next_date == event.starts

    def test_next_date_if_repeats_monthly_after_start_date(self):
        now = timezone.now()
        EventFactory(
            repeats=Event.RepeatChoices.MONTHLY, starts=now - timedelta(days=14),
        )
        first = Event.objects.with_next_date().first()
        assert first.next_date > now
        assert first.next_date.day == 1

    def test_next_date_if_repeats_yearly_before_start_date(self):
        "Should be same as start date if no repeat specified"
        event = EventFactory(
            repeats=Event.RepeatChoices.YEARLY,
            starts=timezone.now() + timedelta(days=14),
        )
        first = Event.objects.with_next_date().first()
        assert first.next_date == event.starts

    def test_next_date_if_repeats_yearly_after_start_date(self):
        "Should be same day and month one year from the date"
        now = timezone.now()
        event = EventFactory(
            repeats=Event.RepeatChoices.YEARLY, starts=now - timedelta(days=14)
        )
        first = Event.objects.with_next_date().first()
        assert first.next_date > now
        assert first.next_date.month == event.starts.month
        assert first.next_date.day == event.starts.day

    def test_relevance_if_starts_in_future(self):
        EventFactory(starts=timezone.now() + timedelta(days=30))

        event = Event.objects.with_next_date().with_relevance().first()
        assert event.relevance == 1

    def test_relevance_if_starts_in_future_and_canceled(self):
        now = timezone.now()
        EventFactory(
            starts=now + timedelta(days=30), canceled=now,
        )

        event = Event.objects.with_next_date().with_relevance().first()
        assert event.relevance == -1

    def test_relevance_if_starts_in_past(self):
        EventFactory(starts=timezone.now() - timedelta(days=30))

        event = Event.objects.with_next_date().with_relevance().first()
        assert event.relevance == 0

    def test_relevance_if_starts_in_past_and_canceled(self):
        now = timezone.now()
        EventFactory(
            starts=now - timedelta(days=30), canceled=now,
        )

        event = Event.objects.with_next_date().with_relevance().first()
        assert event.relevance == -1

    def test_with_timedelta(self):

        now = timezone.now()
        first = EventFactory(starts=now + timedelta(days=30))
        second = EventFactory(starts=now + timedelta(days=15))
        third = EventFactory(starts=now - timedelta(days=20))
        fourth = EventFactory(starts=now - timedelta(days=5))
        fifth = EventFactory(starts=now + timedelta(days=500))

        events = Event.objects.with_next_date().with_timedelta().order_by("timedelta")
        for event in events:
            print(event.starts, event.next_date)

        assert events[0] == fourth
        assert events[1] == second
        assert events[2] == third
        assert events[3] == first
        assert events[4] == fifth

    def test_event_num_attendees_if_none(self, event):
        first = Event.objects.with_num_attendees().first()
        assert first.num_attendees == 0

    def test_event_num_attendees_if_any(self, event, user):
        event.attendees.add(user)
        first = Event.objects.with_num_attendees().first()
        assert first.num_attendees == 1

    def test_is_attending_if_anonymous(self, event, anonymous_user):
        first = Event.objects.is_attending(anonymous_user).first()
        assert not first.is_attending

    def test_is_attending_if_another_event(self, event, user):
        other = EventFactory()
        other.attendees.add(user)
        first = Event.objects.is_attending(user).get(pk=event.id)
        assert not first.is_attending
        second = Event.objects.is_attending(user).get(pk=other.id)
        assert second.is_attending

    def test_is_attending_if_true(self, event, user):
        event.attendees.add(user)
        first = Event.objects.is_attending(user).first()
        assert first.is_attending

    def test_is_attending_if_false(self, event, user):
        first = Event.objects.is_attending(user).first()
        assert not first.is_attending

    def test_with_common_annotations(self, event):
        member = MembershipFactory(community=event.community).member
        first = Event.objects.with_common_annotations(member, event.community).first()
        assert hasattr(first, "is_attending")
        assert hasattr(first, "num_attendees")


class TestEventModel:
    def test_matches_date_if_non_repeating_and_matches_today(self):
        now = timezone.now()
        event = Event(starts=now)
        assert event.matches_date(now)

    def test_matches_date_if_non_repeating_and_not_matching_today(self):
        now = timezone.now()
        event = Event(starts=now - timedelta(days=30))
        assert not event.matches_date(now)

    def test_matches_date_if_repeats_daily(self):
        now = timezone.now()
        event = EventFactory(
            starts=now - timedelta(days=30), repeats=Event.RepeatChoices.DAILY,
        )
        assert event.matches_date(now)

    def test_matches_date_if_repeats_daily_not_started_yet(self):
        now = timezone.now()
        event = Event(
            starts=now + timedelta(days=30), repeats=Event.RepeatChoices.DAILY,
        )
        assert not event.matches_date(now)

    def test_is_repeating_if_repeats_is_null(self):
        event = Event(repeats=None)
        assert not event.is_repeating()

    def test_matches_date_if_repeats_weekly(self):
        # start on Monday
        now = timezone.now()
        # find first day of this week
        event = EventFactory(
            starts=now - timedelta(days=7), repeats=Event.RepeatChoices.WEEKLY,
        )
        dt = now + timedelta(days=7)
        assert event.matches_date(dt)

    def test_matches_date_if_repeats_weekly_wrong_weekday(self):
        # start on Monday
        now = timezone.now()
        # find first day of this week
        event = EventFactory(
            starts=now - timedelta(days=7), repeats=Event.RepeatChoices.WEEKLY,
        )
        dt = now + timedelta(days=5)
        assert not event.matches_date(dt)

    def test_matches_date_if_repeats_monthly_first_of_month(self):
        now = timezone.now()
        event = EventFactory(
            starts=now - timedelta(days=30), repeats=Event.RepeatChoices.MONTHLY,
        )
        dt = (now + timedelta(days=60)).replace(day=1)
        assert event.matches_date(dt)

    def test_matches_date_if_repeats_monthly_not_first_of_month(self):
        now = timezone.now()
        event = EventFactory(
            starts=now - timedelta(days=30), repeats=Event.RepeatChoices.MONTHLY,
        )
        dt = (now + timedelta(days=60)).replace(day=15)
        assert not event.matches_date(dt)

    def test_matches_date_if_repeats_yearly_matches_date(self):
        now = timezone.now()
        event = EventFactory(
            starts=now - timedelta(days=30), repeats=Event.RepeatChoices.YEARLY,
        )
        dt = (now + timedelta(days=400)).replace(
            day=event.starts.day, month=event.starts.month
        )
        assert event.matches_date(dt)

    def test_matches_date_if_repeats_yearly_not_matches_date(self):
        now = timezone.now()
        event = EventFactory(
            starts=now - timedelta(days=30), repeats=Event.RepeatChoices.YEARLY,
        )
        dt = (now + timedelta(days=400)).replace(
            day=event.starts.month, month=event.starts.month
        ) - timedelta(days=1)
        assert not event.matches_date(dt)

    def test_is_repeating_if_repeats_and_repeats_until_is_null(self):
        event = Event(repeats=Event.RepeatChoices.DAILY, repeats_until=None)
        assert event.is_repeating()

    def test_is_repeating_if_repeats_and_repeats_until_gt_current_time(self):
        event = Event(
            repeats=Event.RepeatChoices.DAILY,
            repeats_until=timezone.now() + timedelta(days=30),
        )
        assert event.is_repeating()

    def test_is_repeating_if_repeats_and_repeats_until_lt_current_time(self):
        event = Event(
            repeats=Event.RepeatChoices.DAILY,
            repeats_until=timezone.now() - timedelta(days=30),
        )
        assert not event.is_repeating()

    def test_has_not_started(self):
        event = Event(starts=timezone.now() + timedelta(days=30))
        assert not event.has_started()

    def test_has_started(self):
        event = Event(starts=timezone.now() - timedelta(days=30))
        assert event.has_started()

    def test_is_attendable(self):
        event = EventFactory()
        assert event.is_attendable()

    def test_is_attendable_if_has_started(self):
        event = EventFactory(starts=timezone.now() - timedelta(days=30))
        assert not event.is_attendable()

    def test_is_attendable_if_has_started_if_repeatable(self):
        event = EventFactory(
            starts=timezone.now() - timedelta(days=30),
            repeats=Event.RepeatChoices.DAILY,
        )
        assert event.is_attendable()

    def test_is_attendable_if_has_started_if_repeatable_past_repeats_until(self,):
        now = timezone.now()
        event = EventFactory(
            starts=now - timedelta(days=30),
            repeats=Event.RepeatChoices.DAILY,
            repeats_until=now - timedelta(days=15),
        )
        assert not event.is_attendable()

    def test_is_attendable_if_not_public(self):
        event = EventFactory(published=None)
        assert not event.is_attendable()

    def test_is_attendable_if_deleted(self):
        event = EventFactory(deleted=timezone.now())
        assert not event.is_attendable()

    def test_is_attendable_if_canceled(self):
        event = EventFactory(canceled=timezone.now())
        assert not event.is_attendable()

    def test_get_starts_with_tz(self):
        event = EventFactory(timezone=pytz.timezone("Europe/Helsinki"))
        assert event.get_starts_with_tz().tzinfo.zone == "Europe/Helsinki"

    def test_get_ends_with_tz_if_none(self):
        event = EventFactory(ends=None)
        assert event.get_ends_with_tz() is None

    def test_get_ends_with_tz(self):
        now = timezone.now()
        event = EventFactory(
            ends=now + datetime.timedelta(days=30),
            timezone=pytz.timezone("Europe/Helsinki"),
        )

        assert event.get_ends_with_tz().tzinfo.zone == "Europe/Helsinki"

    def test_get_ends_with_tz_if_repeating(self):
        now = timezone.now()
        EventFactory(
            starts=now,
            repeats=Event.RepeatChoices.MONTHLY,
            ends=now + timedelta(hours=3),
            timezone=pytz.timezone("Europe/Helsinki"),
        )
        first = Event.objects.with_next_date().first()
        assert first.get_ends_with_tz().tzinfo.zone == "Europe/Helsinki"

    def test_get_absolute_url(self, event):
        assert event.get_absolute_url().startswith(f"/events/{event.id}/")

    def test_get_domain_if_no_url(self):
        assert Event().get_domain() == ""

    def test_get_domain_if_url(self):
        assert Event(url="http://google.com").get_domain() == "google.com"

    def test_clean_if_ok(self):
        now = timezone.now()
        event = Event(starts=now, ends=now + timedelta(days=3))
        event.clean()

    def test_clean_if_ends_before_starts(self):
        now = timezone.now()
        event = Event(starts=now, ends=now - timedelta(days=3))
        with pytest.raises(ValidationError):
            event.clean()

    def test_clean_if_repeats_and_end_date_diff_from_start_date(self):
        now = timezone.now().replace(hour=1)
        event = Event(
            starts=now,
            ends=now + timedelta(days=3),
            repeats=Event.RepeatChoices.WEEKLY,
        )
        with pytest.raises(ValidationError):
            event.clean()

    def test_clean_if_repeats_and_repeats_until_before_start_date(self):
        now = timezone.now().replace(hour=1)
        event = Event(
            starts=now,
            ends=now + timedelta(days=3),
            repeats=Event.RepeatChoices.WEEKLY,
            repeats_until=now - timedelta(days=3),
        )
        with pytest.raises(ValidationError):
            event.clean()

    def test_clean_if_repeats_and_repeats_until_ok(self):
        now = timezone.now().replace(hour=1)
        event = Event(
            starts=now,
            ends=now + timedelta(hours=2),
            repeats=Event.RepeatChoices.WEEKLY,
            repeats_until=now + timedelta(days=30),
        )
        event.clean()

    def test_clean_if_repeats_and_repeats_until_none(self):
        now = timezone.now().replace(hour=1)
        event = Event(
            starts=now,
            ends=now + timedelta(hours=2),
            repeats=Event.RepeatChoices.WEEKLY,
            repeats_until=now + timedelta(days=30),
        )
        event.clean()

    def test_get_next_start_date_if_not_repeating(self):
        event = EventFactory(starts=timezone.now())
        assert event.get_next_start_date() == event.starts

    def test_get_next_start_date_if_repeating(self):
        event = EventFactory(starts=timezone.now(), repeats=Event.RepeatChoices.MONTHLY)
        assert (
            Event.objects.with_next_date().first().get_next_start_date() > event.starts
        )

    def test_get_next_end_date_if_not_repeating(self):
        now = timezone.now()
        event = EventFactory(starts=now, ends=now + timedelta(hours=3))
        assert event.get_next_end_date() == event.ends

    def test_get_next_end_date_if_repeating_if_ends_is_None(self):
        EventFactory(
            starts=timezone.now(), repeats=Event.RepeatChoices.MONTHLY, ends=None,
        )
        assert Event.objects.with_next_date().first().get_next_end_date() is None

    def test_get_next_end_date_if_repeating(self):
        now = timezone.now()
        EventFactory(
            starts=now,
            repeats=Event.RepeatChoices.MONTHLY,
            ends=now + timedelta(hours=3),
        )
        first = Event.objects.with_next_date().first()
        dt = first.get_next_end_date()

        assert dt.day == first.next_date.day
        assert dt.month == first.next_date.month
        assert dt.year == first.next_date.year
        assert dt.hour == first.ends.hour
        assert dt.minute == first.ends.minute

    def test_get_location(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.get_location() == "Areenankuja 1, 00240 Helsinki, Uusimaa, Finland"
        ), "location property should include all event location fields"

    def test_get_location_if_empty(self):
        assert Event().get_location() == ""

    def test_get_full_location(self):
        event = Event(
            venue="Hartwall Arena",
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert event.get_full_location() == (
            "Hartwall Arena, Areenankuja 1, 00240 Helsinki, Uusimaa, Finland"
        ), "location should include all event location fields plus venue"

    def test_get_geocoder_location(self):
        event = Event(
            venue="Hartwall Arena",
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert event.get_geocoder_location() == (
            {
                "street": "Areenankuja 1",
                "city": "Helsinki",
                "postalcode": "00240",
                "country": "Finland",
            }
        ), "location should include street, postcode, country name and city"

    def test_get_geocoder_location_if_missing_data(self):
        event = Event(
            venue="Hartwall Arena",
            street_address="Areenankuja 1",
            locality="Helsinki",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.get_geocoder_location() is None
        ), "location should be None if any missing fields"

    def test_location_no_country(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
        )
        assert (
            event.get_location() == "Areenankuja 1, 00240 Helsinki, Uusimaa"
        ), "location property should include all event location fields except country"  # noqa

    def test_partial_location(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.get_location() == "Areenankuja 1, Helsinki, Uusimaa, Finland"
        ), "location property should include all available location fields"

    def test_to_ical(self, event):
        result = force_str(event.to_ical())
        assert "DTSTART" in result

    def test_notify_on_attend_if_owner(self, event):
        assert len(event.notify_on_attend(event.owner)) == 0

    def test_notify_on_attend_if_member(self, event, member):
        notifications = event.notify_on_attend(member.member)
        assert len(notifications) == 1
        assert notifications[0].recipient == event.owner
        assert notifications[0].actor == member.member
        assert notifications[0].verb == "attend"

    def test_notify_on_cancel_if_owner(self, event):
        event.attendees.add(event.owner)
        assert len(event.notify_on_cancel(event.owner)) == 0

    def test_notify_on_cancel_by_moderator_if_owner_attending(self, event, moderator):
        event.attendees.add(event.owner)

        notifications = event.notify_on_cancel(moderator.member)
        assert len(notifications) == 1
        assert notifications[0].recipient == event.owner
        assert notifications[0].actor == moderator.member
        assert notifications[0].verb == "cancel"

    def test_notify_on_cancel_by_moderator_if_owner_not_attending(
        self, event, moderator
    ):
        notifications = event.notify_on_cancel(moderator.member)
        assert len(notifications) == 1
        assert notifications[0].recipient == event.owner
        assert notifications[0].actor == moderator.member
        assert notifications[0].verb == "cancel"

    def test_notify_on_cancel_if_attendee(self, event, member):
        event.attendees.add(member.member)
        notifications = event.notify_on_cancel(event.owner)
        assert len(notifications) == 1
        assert notifications[0].recipient == member.member
        assert notifications[0].actor == event.owner
        assert notifications[0].verb == "cancel"

    def test_notify_on_cancel_if_attendee_not_member(self, event):
        event.attendees.add(UserFactory())
        assert len(event.notify_on_cancel(event.owner)) == 0
