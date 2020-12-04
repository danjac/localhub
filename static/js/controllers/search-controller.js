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
  static values = { param: String };

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

  search(event) {
    event.preventDefault();
    const url = this.hasSelectorTarget
      ? this.selectorTarget.value
      : this.element.getAttribute('action');
    const search = this.inputTarget.value;
    if (url && search) {
      Turbolinks.visit(`${url}?${this.searchParam}=${search}`);
    }
  }

  toggleSelector() {
    if (this.inputTarget.value) {
      this.selectorTarget.removeAttribute('disabled');
    } else {
      this.selectorTarget.setAttribute('disabled', true);
    }
  }

  get searchParam() {
    return this.paramValue || 'q';
  }
}
