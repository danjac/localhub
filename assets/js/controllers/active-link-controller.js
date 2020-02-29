// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  static targets = ['match'];

  connect() {
    const {
      pathname,
      search
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