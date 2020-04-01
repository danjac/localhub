// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
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
    const {
      pathname,
    } = window.location;
    const href =
      (this.element.getAttribute('href') ||
        this.matchTarget.getAttribute('href')).split(/[?#]/)[0];
    const matches = this.data.has('exact') ?
      pathname === href :
      pathname.startsWith(href);
    if (matches) {
      this.element.classList.add(this.data.get('active-class') || 'active');
    }
  }
}
