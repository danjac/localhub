// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

export function confirmDialog(options) {
  /*
  Shortcut to open default confirmation dialog.
  options:
    header: header text
    body: body text
    onConfirm (function): callback if "confirm" button clicked.
  */
  document.getElementById('confirm-dialog')['confirm-dialog'].open(options);
}

function makeAlert(message, level) {
  const tmpl = document.getElementById('alert-template');
  const clone = tmpl.content.cloneNode(true);
  clone.querySelector('div').classList.add(`toast-${level}`);
  clone.querySelector('span').appendChild(document.createTextNode(message));
  document.getElementById('alert-container').appendChild(clone);
}

export const alerts = {
  success: (message) => makeAlert('success'),
  error: (message) => makeAlert('error'),
  warning: (message) => makeAlert('warning'),
  info: (message) => makeAlert('info'),
};
