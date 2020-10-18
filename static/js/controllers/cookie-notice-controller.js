// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { fadeOut } from '~/utils/dom-helpers';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  connect() {
    if (!window.localStorage.getItem('cookie-notice')) {
      this.element.classList.remove('hidden');
    }
  }

  dismiss() {
    window.localStorage.setItem('cookie-notice', true);
    this.element.classList.add('hidden');
  }
}
