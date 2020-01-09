// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  static targets = ['container', 'toggle'];

  connect() {
    // reload container from DOM to get "true" heights
    const container = document.getElementById(this.containerTarget.id);
    console.log('container', container.offsetHeight, container.scrollHeight);

    if (container && container.offsetHeight < container.scrollHeight) {
      this.toggleTarget.classList.remove('d-hide');
    }
  }

  toggle(event) {
    event.preventDefault();
    this.containerTarget.classList.remove('collapsed');
    this.toggleTarget.classList.add('d-hide');
  }
}
