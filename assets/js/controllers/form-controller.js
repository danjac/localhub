// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';
import Turbolinks from 'turbolinks';

import { createAlert } from './alert-controller';

export default class extends Controller {
  /*
  AJAX form controller. Also handles multipart forms, redirects and error messages.

  actions:
    submit: when form is submitted

  data:
    unload: message to display if user tries to navigate away without saving.
      Ignored if not present.

  targets:
    progress: progress bar to show/hide during form processing
  */
  static targets = ['errorMessage', 'errorDetail', 'progress'];

  connect() {
    this.formElements.forEach((element) =>
      element.addEventListener('change', () => this.data.set('changed', true))
    );
  }

  unload(event) {
    const unloadMsg = this.data.get('unload');
    if (this.data.has('changed') && unloadMsg) {
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
    const multipart = this.element.getAttribute('enctype') === 'multipart/form-data';

    this.handleSubmit(method, url, this.serialize(event, multipart));

    return false;
  }

  handleSubmit(method, url, data) {
    if (method === 'GET') {
      Turbolinks.visit(`${url}?${data}`);
      return;
    }

    window.scrollTo(0, 0);

    this.disableFormElements();

    const referrer = location.href;

    axios({
      data,
      headers: {
        'Turbolinks-Referrer': referrer,
      },
      method,
      url,
    })
      .then((response) => {
        window.onbeforeunload = null;
        const contentType = response.headers['content-type'];

        if (contentType.match(/html/)) {
          this.enableFormElements();
          // errors in form, re-render
          Turbolinks.controller.cache.put(
            referrer,
            Turbolinks.Snapshot.wrap(response.data)
          );
          Turbolinks.visit(referrer, {
            action: 'restore',
          });
        } else if (contentType.match(/javascript/)) {
          /* eslint-disable-next-line no-eval */
          eval(response.data);
        }
      })
      .catch((err) => this.handleServerError(err));
  }

  handleServerError(err) {
    this.enableFormElements();
    if (err.response) {
      const { status, statusText } = err.response;
      const errMsg = `${status}: ${statusText}`;
      createAlert(errMsg, 'error');
    }
  }

  disableFormElements() {
    this.toggleProgressBar();
    this.formElements.forEach((el) => el.setAttribute('disabled', true));
  }

  enableFormElements() {
    this.toggleProgressBar();
    this.formElements.forEach((el) => el.removeAttribute('disabled'));
  }

  toggleProgressBar() {
    if (this.progressTarget) {
      this.progressTarget.classList.toggle('d-hide');
    }
  }

  serialize(event, multipart) {
    const data = multipart ? new FormData() : new URLSearchParams();

    this.formElements.forEach((field) => {
      if (field.name && !field.disabled) {
        switch (field.type) {
          case 'reset':
          case 'button':
          case 'submit':
            // if the event is triggered from a button, append the value
            // do this in markup by explictly adding a name/value and
            // data-action="form#submit" to the button
            if (event.target.name === field.name && field.value) {
              data.append(field.name, field.value);
            }
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
              .filter((option) => option.selected)
              .forEach((option) => {
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
