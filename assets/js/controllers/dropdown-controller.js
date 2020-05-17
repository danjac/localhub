// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { maximizeZIndex, fitIntoViewport } from '@/utils/dom-helpers';
import ApplicationController from '@/controllers/application-controller';

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

  toggle(event) {
    event.preventDefault();
    event.stopPropagation();
    this.menuTarget.classList.toggle('hidden');
    maximizeZIndex(fitIntoViewport(this.menuTarget));
  }

  close() {
    this.menuTarget.classList.add('hidden');
  }
}
