// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

const MAX_HEIGHT = 500;

export default class extends Controller {
  static targets = ['container', 'toggle'];

  connect() {
    this.makeCollapsable(false);
    // ensure we check heights of all images and other dynamic elements
    // and handle when these are individually loaded
    for (const tag of ["img", "iframe"]) {
      for (const el of this.containerTarget.getElementsByTagName(tag)) {
        el.onload = () => this.makeCollapsable(true);
      }
    }
  }

  toggle(event) {
    event.preventDefault();
    this.containerTarget.classList.remove('collapsable');
    this.toggleTargets.forEach(el => el.classList.add('d-hide'));
  }

  makeCollapsable(withImage) {
    // show "show more" button if container higher than max height
    if (this.containerTarget.clientHeight > MAX_HEIGHT &&
      !this.containerTarget.classList.contains('collapsable')) {
      console.log(this.containerTarget.clientHeight, 'withImage?', withImage);
      this.containerTarget.classList.add('collapsable');
      this.toggleTargets.forEach(el => el.classList.remove('d-hide'));
    }
  }
}
