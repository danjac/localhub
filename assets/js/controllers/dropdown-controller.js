// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['menu'];

  connect() {
    document.addEventListener('click', (event) => {
      this.close();
    });
  }

  toggle(event) {
    event.preventDefault();
    event.stopPropagation();
    this.element.classList.toggle('active');
    const rect = this.menuTarget.getBoundingClientRect();
    // ensure menu always appears within viewport
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    if (rect.bottom + rect.height > viewportHeight) {
      this.menuTarget.style.top = 'auto';
      this.menuTarget.style.bottom = 0;
    } else {
      this.menuTarget.style.top = 0;
      this.menuTarget.style.bottom = 'auto';
    }
    const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
    if (rect.right + rect.width > viewportWidth) {
      this.menuTarget.style.left = 'auto';
      this.menuTarget.style.right = 0;
    } else {
      this.menuTarget.style.right = 'auto';
      this.menuTarget.style.left = 0;
    }
  }

  close() {
    this.element.classList.remove('active');
  }
}
