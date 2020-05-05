// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Copies content in a hidden or readonly textarea to clipboard.

  actions:
    copy: copies text in selected textarea to clipboard

  targets:
    button: clipboard copy action button
    textarea: readonly textarea to copy
  */
  static targets = ['textarea', 'button'];

  connect() {
    // if clipboard API not supported e.g. on Safari or disabled for security,
    // remove button elements
    if (!navigator.clipboard && this.hasButtonTarget) {
      this.buttonTarget.classList.add('hidden');
    }
  }

  copy(event) {
    event.preventDefault();
    const value = this.textareaTarget.value;
    if (navigator.clipboard && value) {
      navigator.clipboard.writeText(value).then(() => this.confirm());
    }
  }

  confirm() {
    // add temp checkmark to button
    const icon = document.createElement('i');
    icon.classList.add('icon', 'icon-check', 'float-right');
    this.buttonTarget.appendChild(icon);
    const timeout = setTimeout(() => {
      icon.remove();
      clearTimeout(timeout);
    }, 1000);
  }
}
