// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['close'];
  close(event) {
    if (event.which === 27) {
      this.closeTarget.click();
    }
  }
}
