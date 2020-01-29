// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

const BASE_HEIGHT = 300;
const MAX_HEIGHT = BASE_HEIGHT * 1.2;

export default class extends Controller {
  static targets = ['container', 'toggle'];

  connect() {
    this.makeCollapsable();
    // ensure we check heights of all images and other dynamic elements
    // and handle when these are individually loaded
    for (const tag of ["img", "iframe"]) {
      for (const el of this.containerTarget.getElementsByTagName(tag)) {
        el.onload = () => this.makeCollapsable();
      }
    }
  }

  toggle(event) {
    event.preventDefault();
    this.containerTarget.classList.remove('collapsable');
    this.toggleTargets.forEach(el => el.classList.add('d-hide'));
    const originalHeight = parseFloat(this.data.get('originalHeight') || 0);
    if (originalHeight) {
      this.containerTarget.style.height = originalHeight + 'px';
    }
  }

  makeCollapsable() {
    // show "show more" button if container higher than max height
    if (!this.containerTarget.classList.contains('collapsable')) {
      const currentHeight = parseFloat(
        getComputedStyle(this.containerTarget, null).height
      );
      if (currentHeight > MAX_HEIGHT) {
        console.log('currentHeight', currentHeight);
        // store current height
        this.data.set('originalHeight', currentHeight);
        // set new height
        this.containerTarget.style.height = BASE_HEIGHT + 'px';
        this.containerTarget.classList.add('collapsable');
        this.toggleTargets.forEach(el => el.classList.remove('d-hide'));
      }
    }
  }
}
