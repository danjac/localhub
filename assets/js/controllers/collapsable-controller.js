// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  static targets = ['container', 'toggle'];

  connect() {
    this.checkContainerHeight();
    // ensure we check heights of all images
    for (const img of this.containerTarget.getElementsByTagName("img")) {
      img.onload = () => this.checkContainerHeight();
    }
  }

  toggle(event) {
    event.preventDefault();
    this.containerTarget.classList.remove('collapsed');
    this.toggleTarget.classList.add('d-hide');
  }

  checkContainerHeight() {
    if (this.containerTarget.offsetHeight < this.containerTarget.scrollHeight) {
      this.toggleTarget.classList.remove('d-hide');
    }
  }
}
