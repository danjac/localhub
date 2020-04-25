// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Show/hide mobile sidebar navigation elements.

  actions:
    toggle: toggle sidebar/main content elements.

  targets:
    main: main content of application
    nav: sidebar nav element
  */
  static targets = ['main', 'nav'];

  toggle(event) {
    event.preventDefault();
    this.mainTarget.classList.toggle('hide-lg');
    this.navTarget.classList.toggle('hide-lg');
  }
}
