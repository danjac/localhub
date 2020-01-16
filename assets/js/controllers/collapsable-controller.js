// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';


export default class extends Controller {
  static targets = ['container', 'toggle'];

  initialize() {
    document.addEventListener(
      'turbolinks:render', () => this.checkContainerHeights()
    )
  }

  connect() {
    this.checkContainerHeights();
  }

  toggle(event) {
    event.preventDefault();
    this.removeCollapsable();
  }

  checkContainerHeight() {
    // show "show more" button if container higher than max height
    if (this.containerTarget.offsetHeight < this.containerTarget.scrollHeight) {
      this.toggleTargets.forEach(el => el.classList.remove('d-hide'));
    } else {
      this.removeCollapable();
    }
  }

  checkContainerHeights() {
    this.checkContainerHeight();
    // ensure we check heights of all images and other dynamic elements
    // and handle when these are individually loaded
    for (const tag of ["img", "iframe"]) {
      for (const el of this.containerTarget.getElementsByTagName(tag)) {
        el.onload = () => this.checkContainerHeight();
      }
    }

  }

  removeCollapsable() {
    this.containerTarget.classList.remove('collapsable');
    this.toggleTargets.forEach(el => el.classList.add('d-hide'));
  }
}
