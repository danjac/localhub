// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import Cookies from 'js-cookie';
import { Controller } from 'stimulus';

export default class extends Controller {
  /*
  Permanently hides a notice element with a cookie. When
  page is loaded, checks existence of cookie and hides the
  element.

  actions:
    accept: removes element and creates the cookie.

  data:
    name: the cookie name. Should be unique for whole site.
  */
  connect() {
    if (!Cookies.get(this.data.get('name'))) {
      this.element.classList.remove('d-hide');
    }
  }

  accept() {
    Cookies.set(this.data.get('name'), true, {
      domain: window.location.hostname,
      expires: 360,
    });
    this.element.remove();
  }
}
