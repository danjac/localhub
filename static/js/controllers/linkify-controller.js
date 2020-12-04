// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import Turbolinks from 'turbolinks';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  // Makes any non-anchor element linkable with Turbolinks.
  static values = { url: String };

  fetch(event) {
    event.preventDefault();
    Turbolinks.visit(this.urlValue);
  }
}
