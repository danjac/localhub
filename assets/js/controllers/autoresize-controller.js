// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from '@/controllers/application-controller';

export default class extends ApplicationController {
  connect() {
    this.setToScrollHeight();
    this.element.style.overflowY = 'hidden';
  }

  // data-action="autoresize->keyup#resize"
  resize() {
    this.element.style.height = 'auto';
    this.setToScrollHeight();
  }

  setToScrollHeight() {
    this.element.style.height = this.element.scrollHeight + 'px';
  }
}
