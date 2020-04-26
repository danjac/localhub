// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { maxZIndex, getViewport } from '@utils/dom-helpers';
import ApplicationController from './application-controller';

// test comment
export default class extends ApplicationController {
  /*
    Manages dropdown and keeps the menu visible within the viewport.

    actions:
        toggle: toggles the dropdown menu

    targets:
        menu: the dropdown menu
  */
  static targets = ['menu'];

  connect() {
    document.addEventListener('click', () => {
      this.close();
    });
  }

  toggle(event) {
    event.preventDefault();
    event.stopPropagation();
    this.element.classList.toggle('active');

    // ensure menu always appears within viewport
    const viewport = getViewport();
    const rect = this.menuTarget.getBoundingClientRect();

    let top, bottom, left, right;

    if (rect.bottom + rect.height > viewport.height) {
      top = 'auto';
      bottom = 0;
    } else {
      top = 0;
      bottom = 'auto';
    }
    if (rect.left + rect.width > viewport.width) {
      left = 'auto';
      right = 0;
    } else {
      right = 'auto';
      left = 0;
    }
    this.menuTarget.style.top = top;
    this.menuTarget.style.bottom = bottom;
    this.menuTarget.style.left = left;
    this.menuTarget.style.right = right;
    // ensure menu not hidden under another element
    this.menuTarget.style.zIndex = maxZIndex() + 1;
  }

  close() {
    this.element.classList.remove('active');
  }
}
