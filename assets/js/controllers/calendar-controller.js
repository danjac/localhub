// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  addDays,
  addMonths,
  endOfMonth,
  endOfWeek,
  format,
  isAfter,
  isBefore,
  isSameDay,
  parse,
  startOfMonth,
  startOfWeek,
  subMonths,
} from 'date-fns';

import ApplicationController from './application-controller';

const DATE_FORMAT = 'dd/MM/yyyy';
const EVENT_NOTIFY_ON_UPDATE = 'calendar:notify';

export default class extends ApplicationController {
  static targets = [
    'activeTemplate',
    'calendar',
    'dateInput',
    'currentMonth',
    'days',
    'inactiveTemplate',
    'timeInput',
  ];

  connect() {
    if (this.data.has('listen')) {
      this.bus.sub(EVENT_NOTIFY_ON_UPDATE, ({ detail: { startDate, notify } }) => {
        if (notify === this.data.get('listen')) {
          this.data.set('startDate', startDate);
        }
      });
    }
  }

  toggle(event) {
    event.preventDefault();
    if (!this.calendarTarget.classList.toggle('hidden')) {
      const { value } = this.dateInputTarget;
      this.selectedDate = value ? parse(value, DATE_FORMAT, new Date()) : null;

      // first of month date will be selected date OR current-month
      let date;
      if (this.selectedDate) {
        date = this.selectedDate;
      } else if (this.data.has('startDate')) {
        date = parse(this.data.get('startDate'), DATE_FORMAT, new Date());
      } else {
        date = new Date();
      }
      this.firstOfMonthDate = startOfMonth(date);

      this.render();
    }
  }

  nextMonth(event) {
    event.preventDefault();
    this.firstOfMonthDate = addMonths(this.firstOfMonthDate, 1);
    this.render();
  }

  prevMonth(event) {
    event.preventDefault();
    this.firstOfMonthDate = subMonths(this.firstOfMonthDate, 1);
    this.render();
  }

  select(event) {
    event.preventDefault();
    const selectedDate = event.currentTarget.getAttribute(
      `data-${this.identifier}-date`
    );
    this.dateInputTarget.value = selectedDate;
    this.calendarTarget.classList.add('hidden');
    if (this.data.has('notify')) {
      this.bus.pub(EVENT_NOTIFY_ON_UPDATE, {
        startDate: selectedDate,
        notify: this.data.get('notify'),
      });
    }
    if (this.timeInputTarget.value === '') {
      if (this.data.has('defaultTime')) {
        this.timeInputTarget.value = this.data.get('defaultTime');
      }
      this.timeInputTarget.focus();
    }
  }

  render() {
    const lastOfMonthDate = endOfMonth(this.firstOfMonthDate);
    const startDate = startOfWeek(this.firstOfMonthDate);
    const endDate = endOfWeek(lastOfMonthDate);
    const today = new Date();

    // set the current month first (tbd: i18n)
    this.currentMonthTarget.innerText = format(this.firstOfMonthDate, 'MMMM yyyy');
    // clear
    while (this.daysTarget.firstChild) {
      this.daysTarget.removeChild(this.daysTarget.firstChild);
    }
    // render each day
    let date = startDate;
    while (isBefore(date, endDate)) {
      let clone;
      if (isBefore(date, this.firstOfMonthDate) || isAfter(date, lastOfMonthDate)) {
        clone = this.inactiveTemplateTarget.content.cloneNode(true);
      } else {
        clone = this.activeTemplateTarget.content.cloneNode(true);

        const btn = clone.querySelector('button');

        btn.append(date.getDate().toString());

        const calendarItem = clone.querySelector('.calendar-item');
        calendarItem.setAttribute(
          `data-${this.identifier}-date`,
          format(date, DATE_FORMAT)
        );

        if (isSameDay(date, today)) {
          calendarItem.classList.add('bg-gray-100');
        }

        if (this.selectedDate && isSameDay(date, this.selectedDate)) {
          calendarItem.classList.add('bg-gray-200', 'font-semibold');
        }
      }

      this.daysTarget.append(clone);

      date = addDays(date, 1);
    }
  }
}
