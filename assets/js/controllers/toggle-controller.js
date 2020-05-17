// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from '@/controllers/application-controller';

export default class extends ApplicationController {
  /*
  Toggles one or more elements using hidden class or another class.

  actions:
    toggle: toggles hidden on all togglable targets.

  targets:
    togglable: elements to be toggled.
  */
  static targets = ['togglable'];

  toggle(event) {
    event.preventDefault();
    const toggleClass = this.data.get('class') || 'hidden';
    this.togglableTargets.forEach((el) => el.classList.toggle(toggleClass));
  }
}
