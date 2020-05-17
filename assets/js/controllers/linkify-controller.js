// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import Turbolinks from 'turbolinks';

import ApplicationController from '@/controllers/application-controller';

export default class extends ApplicationController {
  // Makes any non-anchor element linkable with Turbolinks.

  fetch(event) {
    event.preventDefault();
    Turbolinks.visit(this.data.get('url'));
  }
}
