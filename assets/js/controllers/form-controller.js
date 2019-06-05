// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

export default class extends Controller {
  submit(event) {
    event.preventDefault();

    const method = this.element.getAttribute('method');
    const url = this.element.getAttribute('action');
    const multipart =
      this.element.getAttribute('enctype') === 'multipart/form-data';

    const data = this.serialize(multipart);

    this.formElements.forEach(el => el.setAttribute('disabled', true));

    if (method === 'GET') {
      return Turbolinks.visit(`${url}?${data}`);
    }

    const referrer = location.href;

    axios({
      data,
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    }).then(response => {
      const contentType = response.headers['content-type'];

      if (contentType.match(/html/)) {
        this.formElements.forEach(el => el.removeAttribute('disabled'));
        // errors in form, re-render
        Turbolinks.controller.cache.put(
          referrer,
          Turbolinks.Snapshot.wrap(response.data)
        );
        Turbolinks.visit(referrer, { action: 'restore' });
      } else if (contentType.match(/javascript/)) {
        /* eslint-disable-next-line no-eval */
        eval(response.data);
      }
    });
    return false;
  }

  serialize(multipart) {
    const data = multipart ? new FormData() : new URLSearchParams();

    this.formElements.forEach(field => {
      if (field.name && !field.disabled) {
        switch (field.type) {
          case 'reset':
          case 'button':
          case 'submit':
            break;
          case 'file':
            if (multipart) {
              data.append(field.name, field.files[0]);
            }
            break;
          case 'radio':
          case 'checkbox':
            if (field.checked) {
              data.append(field.name, field.value);
            }
            break;
          case 'select-multiple':
            Array.from(field.options)
              .filter(option => option.selected)
              .forEach(option => {
                data.append(field.name, option.value);
              });
            break;
          default:
            data.append(field.name, field.value);
        }
      }
    });
    return data;
  }

  get formElements() {
    return Array.from(this.element.elements);
  }
}
