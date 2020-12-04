// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Highlights an active menu item, tab etc with "active" class on
  page load.

  data:
    active-class: the CSS class used to indicate active (default: 'active')
    exact: match the exact URL (including query string and full path)
      (default: false)
  */
  static targets = ['match'];
  static classes = ['active'];
  static values = { regex: String, exact: Boolean };

  connect() {
    const { pathname } = window.location;

    const href = (
      this.element.getAttribute('href') || this.matchTarget.getAttribute('href')
    ).split(/[?#]/)[0];

    const matches = this.hasExactValue
      ? pathname === href
      : this.hasRegexValue
      ? pathname.match(this.regexValue)
      : pathname.startsWith(href);
    if (matches) {
      this.classList.add(this.activeClass);
    }
  }
}
