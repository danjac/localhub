// Copyright (c) 2019 by Dan Jacob
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
  subMonths
} from 'date-fns';

import { Controller } from 'stimulus';

const DATE_FORMAT = 'dd/MM/yyyy';

export default class extends Controller {
  static targets = ['calendar', 'dateInput', 'currentMonth', 'days'];

  toggle(event) {
    event.preventDefault();
    if (!this.calendarTarget.classList.toggle('d-none')) {
      const { value } = this.dateInputTarget;

      this.selectedDate = value ? parse(value, DATE_FORMAT, new Date()) : null;
      this.firstOfMonthDate = startOfMonth(this.selectedDate || new Date());

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
    const selectedDate = event.currentTarget.getAttribute('data-calendar-date');
    this.dateInputTarget.value = selectedDate;
    this.calendarTarget.classList.add('d-none');
  }

  render() {
    const lastOfMonthDate = endOfMonth(this.firstOfMonthDate);
    const startDate = startOfWeek(this.firstOfMonthDate);
    const endDate = endOfWeek(lastOfMonthDate);
    const today = new Date();
    // set the current month first (tbd: i18n)
    this.currentMonthTarget.innerText = format(
      this.firstOfMonthDate,
      'MMMM yyyy'
    );
    // clear
    while (this.daysTarget.firstChild) {
      this.daysTarget.removeChild(this.daysTarget.firstChild);
    }
    // render each day
    let date = startDate;
    while (isBefore(date, endDate)) {
      const btn = document.createElement('button');

      btn.append(date.getDate().toString());
      btn.setAttribute('data-action', 'calendar#select');
      btn.setAttribute('data-calendar-date', format(date, DATE_FORMAT));

      btn.classList.add('date-item');

      if (isSameDay(date, today)) {
        btn.classList.add('date-today');
      }

      if (this.selectedDate && isSameDay(date, this.selectedDate)) {
        btn.classList.add('badge');
      }
      // insert into DOM
      const div = document.createElement('div');
      div.classList.add('calendar-date');
      if (isBefore(date, this.firstOfMonthDate)) {
        div.classList.add('prev-month');
      } else if (isAfter(date, lastOfMonthDate)) {
        div.classList.add('next-month');
      }
      div.append(btn);
      this.daysTarget.append(div);

      date = addDays(date, 1);
    }
  }
}
