// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import * as classList from '~/utils/class-list';

import ApplicationController from './application-controller';

const MAX_HEIGHT = 360;

export default class extends ApplicationController {
  /*
  Renders a collapsable element that can be expanded with a "Show more" button.

  actions:
    toggle: switches the collapsable state

  targets:
    container: element containing the collapsable content
    toggle: elements to show/hide depending on collapsable state
  */
  static targets = ['container', 'toggle'];
  static classes = ['collapsed'];
  static values = { collapsed: Boolean };

  connect() {
    this.check();
  }

  disconnect() {
    if (this.observer) {
      this.observer.disconnect(this.containerTarget);
    }
  }

  check() {
    if (ResizeObserver) {
      this.observer = new ResizeObserver((entries) => {
        for (const entry of entries) {
          this.makeCollapsable(entry.contentRect.height);
        }
      });
      this.observer.observe(this.containerTarget);
    }
  }

  toggle(event) {
    if (this.collapsedValue) {
      event.preventDefault();
      event.stopPropagation();
      this.removeCollapsable();
    }
  }

  removeCollapsable() {
    classList.remove(this.containerTarget, this.collapsedClass);
    this.toggleTargets.forEach((el) => el.classList.add('hidden'));
    this.observer.disconnect(this.containerTarget);
    this.collapsedValue = false;
  }

  makeCollapsable(height) {
    if (height > MAX_HEIGHT && !this.isCollapsable) {
      classList.add(this.containerTarget, this.collapsedClass);
      this.containerTarget.style.maxHeight = MAX_HEIGHT;
      this.toggleTargets.forEach((target) => target.classList.remove('hidden'));
      this.collapsedValue = true;
    }
  }
}
