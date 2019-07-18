// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios, { AxiosResponse } from 'axios';
import Turbolinks from 'turbolinks';

import { HTMLFieldElement } from '../types';

// should be prop
const unloadMsg =
  'Are you sure you want to leave this page? All your changes will be lost.';

export default class extends Controller {
  connect() {
    this.formElements.forEach(element =>
      element.addEventListener('change', () =>
        this.data.set('changed', 'changed')
      )
    );
  }

  unload(event: Event) {
    if (this.data.has('changed')) {
      if (event.type === 'turbolinks:before-visit') {
        if (!window.confirm(unloadMsg)) {
          event.preventDefault();
          return false;
        }
        return true;
      }
      event.returnValue = true;
      return event.returnValue;
    }
    return true;
  }

  submit(event: Event) {
    const method = this.element.getAttribute('method');
    event.preventDefault();

    this.data.delete('changed');

    const url = this.element.getAttribute('action');
    const multipart =
      this.element.getAttribute('enctype') === 'multipart/form-data';

    const data = this.serialize(multipart);

    this.handleRequest(data, method, url);
  }

  handleRequest(data: any, method: string, url: string) {
    if (method === 'GET') {
      return Turbolinks.visit(`${url}?${data}`);
    }

    this.formElements.forEach(el => el.setAttribute('disabled', 'disabled'));

    axios
      .request({
        data,
        headers: {
          'Turbolinks-Referrer': location.href
        },
        method: 'POST',
        url
      })
      .then((response: AxiosResponse) => {
        window.onbeforeunload = null;
        const contentType = response.headers['content-type'];

        if (contentType.match(/html/)) {
          this.formElements.forEach(el => el.removeAttribute('disabled'));
          // errors in form, re-render
            // Turbolinks.controller.cache.put(
            // referrer,
            // Snapshot.wrap(response.data)
            // );
          Turbolinks.visit(location.href, { action: 'restore' });
        } else if (contentType.match(/javascript/)) {
          /* eslint-disable-next-line no-eval */
          eval(response.data);
        }
      });
    return false;
  }

  serialize(multipart: Boolean): any {
    const data = multipart ? new FormData() : new URLSearchParams();

    this.formElements.forEach((field: HTMLFieldElement) => {
      if (field.name && !field.disabled) {
        switch (field.type) {
          case 'reset':
          case 'button':
          case 'submit':
            break;
          case 'file':
            if (multipart && field instanceof HTMLInputElement) {
              data.append(field.name, field.files[0]);
            }
            break;
          case 'radio':
          case 'checkbox':
            if (field instanceof HTMLInputElement && field.checked) {
              data.append(field.name, field.value);
            }
            break;
          case 'select-multiple':
            if (field instanceof HTMLSelectElement) {
              Array.from(field.options)
                .filter((option: HTMLOptionElement) => option.selected)
                .forEach((option: HTMLOptionElement) => {
                  data.append(field.name, option.value);
                });
            }
            break;
          default:
            data.append(field.name, field.value);
        }
      }
    });
    return data;
  }

  get formElements(): Array<Element> {
    if (this.element instanceof HTMLFormElement) {
      return Array.from(this.element.elements);
    }
    return [];
  }

  set changed(isChanged: Boolean) {
    if (isChanged) {
      this.data.set('changed', 'changed');
    } else {
      this.data.delete('changed');
    }
  }

  get changed(): Boolean {
    return this.data.has('changed');
  }
}
