// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import Cookies from 'js-cookie';
import {
  Controller
} from 'stimulus';

export default class extends Controller {
  connect() {
    if (!Cookies.get(this.data.get('name'))) {
      this.element.classList.remove('d-hide');
    }
  }

  accept() {
    Cookies.set(this.data.get('name'), true, {
      domain: window.location.hostname,
      expires: 360
    });
    this.element.remove();
  }
}