// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  /*
  Toggles one or more elements using d-none class or another class.

  actions:
    toggle: toggles d-none on all togglable targets.

  targets:
    togglable: elements to be toggled.
  */
  static targets = ['togglable'];

  toggle(event) {
    event.preventDefault();
    const toggleClass = this.data.get('class') || 'd-none';
    this.togglableTargets.forEach((el) => el.classList.toggle(toggleClass));
  }
}
