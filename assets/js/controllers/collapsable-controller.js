// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  static targets = ['container', 'toggle'];

  connect() {
    console.log(this.containerTarget.offsetHeight, this.containerTarget.scrollHeight);
    if (this.containerTarget.offsetHeight < this.containerTarget.scrollHeight) {
      this.toggleTarget.classList.remove('d-hide');
    }
  }

  toggle(event) {
    event.preventDefault();
    this.containerTarget.classList.remove('collapsed');
    this.toggleTarget.classList.add('d-hide');
  }
}
