// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

const MAX_HEIGHT = 300;

export default class extends Controller {
  static targets = ['container', 'toggle'];

  connect() {
    this.makeCollapsable();
    // ensure we check heights of all images and other dynamic elements
    // and handle when these are individually loaded
    //for (const tag of ["img", "iframe"]) {
      //for (const el of this.containerTarget.getElementsByTagName(tag)) {
        //el.onload = () => this.makeCollapsable();
      //}
    //}
  }

  toggle(event) {
    event.preventDefault();
    this.containerTarget.classList.remove('collapsable');
    this.toggleTargets.forEach(el => el.classList.add('d-hide'));
  }

  makeCollapsable() {
    // show "show more" button if container higher than max height
    if (!this.containerTarget.classList.contains('collapsable')) {
      const currentHeight = parseFloat(
        getComputedStyle(this.containerTarget, null).height
      );
      if (currentHeight > MAX_HEIGHT) {
        this.containerTarget.classList.add('collapsable');
        this.toggleTargets.forEach(el => el.classList.remove('d-hide'));
      }
    }
  }
}
