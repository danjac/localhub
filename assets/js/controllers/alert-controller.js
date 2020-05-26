// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { fadeOut } from '@/utils/dom-helpers';
import ApplicationController from './application-controller';

const TIMEOUT = 3000;

export default class extends ApplicationController {
  /*
  Used with an server-side rendered alert element that "fades out" after a few seconds
  after page load.

  data:
    remove-after: number of milliseconds (default: 5000)
  */
  connect() {
    const removeAfter = parseInt(this.data.get('remove-after') || TIMEOUT, 10);
    this.timeout = setTimeout(() => {
      this.dismiss();
      clearTimeout(this.timeout);
    }, removeAfter);
  }

  dismiss() {
    fadeOut(this.element, () => this.element.remove());
  }
}
