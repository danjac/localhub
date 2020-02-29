// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  decrement() {
    const counters = (this.data.get('counters') || '').split(',');
    counters.forEach(counter => {
      const el = document.getElementById(counter.trim());
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
    })
  }
}