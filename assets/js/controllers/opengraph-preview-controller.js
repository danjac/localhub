// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import {
  EVENT_FORM_COMPLETE,
  EVENT_FORM_FETCHING,
  TOAST_ERROR,
} from '@utils/application-constants';

import ApplicationController from './application-controller';

const EVENT_OPENGRAPH_UPDATE = 'opengraph:update';
const EVENT_OPENGRAPH_CLEAR = 'opengraph:clear';

export default class extends ApplicationController {
  static targets = [
    'description',
    'image',
    'input',
    'missingDescription',
    'missingImage',
    'title',
  ];

  connect() {
    if (this.data.has('subscriber')) {
      this.subscribe(EVENT_OPENGRAPH_UPDATE, ({ detail: { name, value } }) => {
        if (name === this.data.get('subscriber')) {
          this.inputTarget.value = value;
        }
      });
      this.subscribe(EVENT_OPENGRAPH_CLEAR, () => {
        this.inputTarget.value = '';
      });
    }
  }

  change(event) {
    const { currentTarget } = event;

    this.titleTarget.classList.add('d-none');
    this.imageTarget.classList.add('d-none');
    this.descriptionTarget.classList.add('d-none');

    this.titleTarget.innerText = '';
    this.descriptionTarget.innerText = '';
    this.imageTarget.setAttribute('src', '');
    this.missingDescriptionTarget.classList.add('d-none');
    this.missingImageTarget.classList.add('d-none');

    const url = event.currentTarget.value;

    if (!url) {
      this.clearSubscribers();
      return;
    }

    currentTarget.setAttribute('disabled', true);
    this.disableFormControls();

    axios
      .get(this.data.get('preview-url'), { params: { url } })
      .then((response) => {
        const { title, description, image } = response.data;

        if (title) {
          this.titleTarget.innerText = title;
          this.titleTarget.classList.remove('d-none');
        }
        if (description) {
          this.descriptionTarget.innerText = description;
          this.descriptionTarget.classList.remove('d-none');
        } else {
          this.descriptionTarget.classList.add('d-none');
          this.missingDescriptionTarget.classList.remove('d-none');
        }
        if (image) {
          this.imageTarget.setAttribute('src', image);
          this.imageTarget.classList.remove('d-none');
        } else {
          this.imageTarget.classList.add('d-none');
          this.missingImageTarget.classList.remove('d-none');
        }
        this.updateSubscribers({ title, image, description });
      })
      .catch((err) => this.handleServerError(err))
      .finally(() => {
        this.enableFormControls();
        currentTarget.removeAttribute('disabled');
      });
  }

  disableFormControls() {
    this.publish(EVENT_FORM_FETCHING);
  }

  enableFormControls() {
    this.publish(EVENT_FORM_COMPLETE);
  }

  clearSubscribers() {
    this.publish(EVENT_OPENGRAPH_CLEAR);
  }

  updateSubscribers(data) {
    Object.keys(data).forEach((name) => {
      this.publish(EVENT_OPENGRAPH_UPDATE, { name, value: data[name] });
    });
  }

  handleServerError(err) {
    // TBD: we probably just want an error field
    this.clearSubscribers();
    if (err.response) {
      const { status, statusText } = err.response;
      this.toast(TOAST_ERROR, `${status}: ${statusText}`);
    }
  }
}
