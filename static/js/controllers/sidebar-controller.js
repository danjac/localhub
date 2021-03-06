// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['main', 'nav'];

  toggle(event) {
    event.preventDefault();
    this.mainTarget.classList.toggle('hidden');
    this.navTargets.forEach((el) => el.classList.toggle('hidden'));
  }

  reset() {
    this.mainTarget.classList.remove('hidden');
    this.navTargets.forEach((el) => el.classList.add('hidden'));
  }
}
