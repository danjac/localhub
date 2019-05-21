// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['chooser'];

  open(event) {
    event.preventDefault();
    this.chooserTarget.classList.toggle('d-none');
  }
}
