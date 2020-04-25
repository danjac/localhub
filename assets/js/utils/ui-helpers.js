// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

function makeAlert(level) {
  return (message) => {
    const tmpl = document.getElementById('alert-template');
    const clone = tmpl.content.cloneNode(true);
    clone.querySelector('div').classList.add(`toast-${level}`);
    clone.querySelector('span').appendChild(document.createTextNode(message));
    document.getElementById('alert-container').appendChild(clone);
  };
}

export const alerts = {
  success: makeAlert('success'),
  error: makeAlert('error'),
  warning: makeAlert('warning'),
  info: makeAlert('info'),
};
