// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from '@/controllers/application-controller';

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

  connect() {
    const { pathname } = window.location;

    const href = (
      this.element.getAttribute('href') || this.matchTarget.getAttribute('href')
    ).split(/[?#]/)[0];

    const regex = this.data.get('regex');

    const matches = this.data.has('exact')
      ? pathname === href
      : regex
      ? pathname.match(regex)
      : pathname.startsWith(href);
    if (matches) {
      this.classList.add(this.data.get('active-class') || 'active');
    }
  }
}
