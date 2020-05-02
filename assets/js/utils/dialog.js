// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { EVENT_CONFIRM_OPEN } from '@utils/application-constants';

export default class {
  constructor(controller) {
    this.controller = controller;
  }

  confirm(options) {
    this.controller.publish(EVENT_CONFIRM_OPEN, options);
  }
}
