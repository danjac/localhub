// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Toggles one or more elements using hidden class.
  */
  static targets = ['togglable'];

  toggle(event) {
    event.preventDefault();
    this.togglableTargets.forEach((el) => el.classList.toggle('hidden'));
  }
}
