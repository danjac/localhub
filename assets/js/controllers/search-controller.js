// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import Turbolinks from 'turbolinks';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Handles search dropdown selector.

  actions:
      change: if search query changes
      select: if search selector changes: redirects to the new search page

  data:
      param: query string parameter (default: "q")

  targets:
      input: text <input> element for the search query
      selector: <select> element showing all search options
  */
  static targets = ['input', 'selector'];

  connect() {
    if (this.hasSelectorTarget) {
      this.toggleSelector();
      const { pathname } = window.location;
      for (const option of this.selectorTarget.options) {
        if (option.value === pathname) {
          option.setAttribute('selected', true);
        }
      }
    }
  }

  change() {
    this.toggleSelector();
  }

  select() {
    const { value } = this.selectorTarget;
    const param = this.data.get('param') || 'q';
    const search = this.inputTarget.value;
    if (value && search) {
      Turbolinks.visit(`${value}?${param}=${search}`);
    }
  }

  submit() {
    const param = this.data.get('param') || 'q';
    const search = this.inputTarget.value;
    if (search) {
      Turbolinks.visit(`${value}?${param}=${search}`);
    }
  }

  toggleSelector() {
    if (!!this.inputTarget.value) {
      this.selectorTarget.removeAttribute('disabled');
    } else {
      this.selectorTarget.setAttribute('disabled', true);
    }
  }
}
