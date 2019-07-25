// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

// should be prop
const unloadMsg =
  'Are you sure you want to leave this page? All your changes will be lost.';

export default class extends Controller {
  connect() {
    this.formElements.forEach(element =>
      element.addEventListener('change', () => this.data.set('changed', true))
    );
  }

  unload(event) {
    if (this.data.has('changed')) {
      if (event.type === 'turbolinks:before-visit') {
        if (!window.confirm(unloadMsg)) {
          event.preventDefault();
          return false;
        }
        return true;
      }
      event.returnValue = unloadMsg;
      return event.returnValue;
    }
    return true;
  }

  submit(event) {
    event.preventDefault();

    this.data.delete('changed');

    const method = this.element.getAttribute('method');
    const url = this.element.getAttribute('action');
    const multipart =
      this.element.getAttribute('enctype') === 'multipart/form-data';

    this.handleSubmit(method, url, this.serialize(multipart));

    return false;
  }

  handleSubmit(method, url, data) {
    if (method === 'GET') {
      Turbolinks.visit(`${url}?${data}`);
      return;
    }

    this.disableFormElements();
    const referrer = location.href;

    axios({
      data,
      headers: {
        'Turbolinks-Referrer': referrer
      },
      method,
      url
    })
      .then(response => {
        window.onbeforeunload = null;
        const contentType = response.headers['content-type'];

        if (contentType.match(/html/)) {
          this.enableFormElements();
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
      })
      .catch(() => {
        // we need something more elaborate later
        this.enableFormElements();
      });
  }

  disableFormElements() {
    this.formElements.forEach(el => el.setAttribute('disabled', true));
  }

  enableFormElements() {
    this.formElements.forEach(el => el.removeAttribute('disabled'));
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

  set changed(isChanged) {
    this.data.set('changed', isChanged);
  }

  get changed() {
    return this.data.get('changed') === true;
  }
}
