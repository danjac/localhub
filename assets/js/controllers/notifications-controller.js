// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import ApplicationController from '@/controllers/application-controller';

export default class extends ApplicationController {
  static targets = ['notification'];

  dismiss(event) {
    event.preventDefault();

    const url = event.currentTarget.getAttribute(
      `data-${this.identifier}-mark-read-url`
    );

    if (url) {
      axios.post(url);
    }

    this.notificationTargets[0].remove();

    if (this.hasNotificationTarget) {
      this.notificationTargets[0].classList.remove('hidden');
    } else {
      this.element.remove();
    }
  }
}
