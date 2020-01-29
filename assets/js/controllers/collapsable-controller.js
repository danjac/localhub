// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

const MAX_HEIGHT = 360;

export default class extends Controller {
  static targets = ['container', 'toggle'];

  connect() {
    if (ResizeObserver) {
      this.observer = new ResizeObserver(entries => {
        for (const entry of entries) {
          console.log(entry);
          this.makeCollapsable(entry.contentRect.height);
        }
      });
      this.observer.observe(this.containerTarget);
    }
  }

  disconnect() {
    if (this.observer) {
      this.observer.disconnect(this.containerTarget);
    }
  }

  toggle(event) {
    event.preventDefault();
    this.removeCollapsable();
  }

  removeCollapsable() {
    this.containerTarget.classList.remove('collapsable');
    this.toggleTargets.forEach(el => el.classList.add('d-hide'));
    this.observer.disconnect(this.containerTarget);
  }

  makeCollapsable(height) {
    if (height > MAX_HEIGHT &&
      !this.containerTarget.classList.contains('collapsable')) {
      this.containerTarget.classList.add('collapsable');
      this.toggleTargets.forEach(
        target => target.classList.remove('d-hide')
      );
    }
  }
}
