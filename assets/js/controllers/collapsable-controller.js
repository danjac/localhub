// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

const MAX_HEIGHT = 360;

export default class extends Controller {
  /*
  Renders a collapsable element that can be expanded with a "Show more" button.

  actions:
    toggle: switches the collapsable state

  targets:
    container: element containing the collapsable content
    toggle: elements to show/hide depending on collapsable state
  */
  static targets = ['container', 'toggle'];

  connect() {
    if (ResizeObserver) {
      this.observer = new ResizeObserver(entries => {
        for (const entry of entries) {
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
    if (this.isCollapsable) {
      event.preventDefault();
      event.stopPropagation();
      this.removeCollapsable();
    }
  }

  removeCollapsable() {
    this.containerTarget.classList.remove('collapsable');
    this.toggleTargets.forEach(el => el.classList.add('d-hide'));
    this.observer.disconnect(this.containerTarget);
  }

  makeCollapsable(height) {
    if (height > MAX_HEIGHT && !this.isCollapsable) {
      this.containerTarget.classList.add('collapsable');
      this.toggleTargets.forEach(
        target => target.classList.remove('d-hide')
      );
    }
  }

  get isCollapsable() {
    return this.containerTarget.classList.contains("collapsable");
  }
}
