// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

export default function (options) {
  /*
  Shortcut to open default confirmation dialog.
  options:
    header: header text
    body: body text
    onConfirm (function): callback if "confirm" button clicked.
  */
  document.getElementById('confirm-dialog')['confirm-dialog'].open(options);
}


