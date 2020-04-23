// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

// client-side alerts
export function createAlert(message, level) {
  const tmpl = document.getElementById('alert-template');
  const clone = tmpl.content.cloneNode(true);
  clone.querySelector('div').classList.add(`toast-${level}`);
  clone.querySelector('span').appendChild(document.createTextNode(message));
  document.getElementById('alert-container').appendChild(clone);
}

export const success = message => createAlert(message, 'success');
export const error = message => createAlert(message, 'error');
export const warning = message => createAlert(message, 'warning');
export const info = message => createAlert(message, 'info');
