// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

const MAX_HEIGHT = 300;

export default class extends Controller {
  static targets = ['container', 'toggle'];

  connect() {
    const style = window.getComputedStyle(this.containerTarget, null);
    const height = style && style.height ? parseInt(style.height, 10) : 0;
    console.log("container", style, height)

    if (height >= MAX_HEIGHT) {
      this.toggleTarget.classList.remove('d-hide');
    }
  }

  toggle(event) {
    event.preventDefault();
    this.containerTarget.classList.remove('collapsed');
    this.toggleTarget.classList.add('d-hide');
  }
}
