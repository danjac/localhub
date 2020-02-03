// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  decrement() {
    const id = this.data.get('id');
    if (!id) {
      return;
    }

    const el = document.getElementById(id);
    const value = el && el.dataset.badge;
    if (value) {
      const newValue = parseInt(value, 10) - 1;
      if (newValue) {
        el.dataset.badge = newValue;
      } else {
        delete el.dataset.badge;
        el.classList.remove('badge');
      }
    }
  }
}
