// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  static targets = ['togglable'];

  toggle(event) {
    event.preventDefault();

    const targetAttr = `data-${this.data.identifier}-target`;
    const target = event.currentTarget.getAttribute(targetAttr);

    this.togglableTargets
      .filter(el => el.getAttribute(targetAttr) === target)
      .forEach(el => el.classList.toggle('d-hide'));
  }
}