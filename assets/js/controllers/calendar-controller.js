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

import { Controller } from 'stimulus';

const DATE_FORMAT = 'dd/MM/yyyy';

export default class extends Controller {
  /*
  Renders an HTML calendar. Used with a date <input> widget.

  actions:
    toggle: re-renders or hides the calendar.
    select: select a specific date and insert into dateInput.

  targets:
    calendar: the calendar container element
    dateInput: <input> tag triggering the input.
    currentMonth: element rendering the current month.
    days: elements rendering each day.
    template: HTML <template> to render the calendar body.
  */
  static targets = ['calendar', 'dateInput', 'currentMonth', 'days', 'template'];

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
    const selectedDate = event.currentTarget.getAttribute(
      `data-${this.identifier}-date`
    );
    this.dateInputTarget.value = selectedDate;
    this.calendarTarget.classList.add('d-none');
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
      const clone = this.templateTarget.content.cloneNode(true);

      const div = clone.querySelector('div');
      const btn = clone.querySelector('button');

      btn.append(date.getDate().toString());
      btn.setAttribute(`data-${this.identifier}-date`, format(date, DATE_FORMAT));

      if (isSameDay(date, today)) {
        btn.classList.add('date-today');
      }

      if (this.selectedDate && isSameDay(date, this.selectedDate)) {
        btn.classList.add('badge');
      }
      // insert into DOM
      if (isBefore(date, this.firstOfMonthDate)) {
        div.classList.add('prev-month');
      } else if (isAfter(date, lastOfMonthDate)) {
        div.classList.add('next-month');
      }
      this.daysTarget.append(clone);

      date = addDays(date, 1);
    }
  }
}
