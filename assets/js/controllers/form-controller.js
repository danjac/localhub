// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import Turbolinks from 'turbolinks';

import { Events } from '~/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  connect() {
    this.formElements.forEach((element) =>
      element.addEventListener('change', () => this.data.set('changed', true))
    );

    this.bus.sub(Events.FORM_FETCHING, () => this.disableFormControls());
    this.bus.sub(Events.FORM_COMPLETE, () => this.enableFormControls());
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

    const data = new FormData(this.element);

    // add button element value if any
    const { currentTarget } = event;

    if (currentTarget.nodeName === 'BUTTON') {
      data.append(currentTarget.getAttribute('name'), currentTarget.value);
    }

    this.handleSubmit(method, url, data);

    return false;
  }

  handleSubmit(method, url, data) {
    if (this.data.has('disabled')) {
      return;
    }

    this.bus.pub(Events.FORM_FETCHING);

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
          // errors in form, re-render
          this.bus.pub(Events.FORM_COMPLETE);
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
      .catch((err) => {
        this.bus.pub(Events.FORM_COMPLETE);
        if (err.response) {
          const { status, statusText } = err.response;
          this.toaster.error(`${status}: ${statusText}`);
        }
      });
  }

  disableFormControls() {
    window.scrollTo(0, 0);
    this.data.set('disabled', true);
    this.formElements.forEach((el) => el.setAttribute('disabled', true));
  }

  enableFormControls() {
    this.data.delete('disabled');
    this.formElements.forEach((el) => el.removeAttribute('disabled'));
  }

  get formElements() {
    return Array.from(this.element.elements);
  }
}
