// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  /*
  simple controller that shows an element
  if JS enabled: we can hide actions not
  normally available to JS-disabled browsers.
  ensure element has class d-hide.

  data:
    ignore: if set then will not automatically show the element on load
      (default: false)
  */
  connect() {
    if (!this.data.has('ignore')) {
      this.element.classList.remove('d-hide');
    }
  }
}
