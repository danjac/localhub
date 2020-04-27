// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { TOAST_ERROR } from '@utils/constants';
import ApplicationController from './application-controller';

const EVENT_OPENGRAPH_UPDATE = 'opengraph:update';
const EVENT_OPENGRAPH_FETCHING = 'opengraph:fetching';
const EVENT_OPENGRAPH_COMPLETE = 'opengraph:complete';
const EVENT_OPENGRAPH_CLEAR = 'opengraph:clear';

export default class extends ApplicationController {
  static targets = [
    'image',
    'description',
    'title',
    'input',
    'missingImage',
    'missingDescription',
  ];

  connect() {
    if (this.data.has('subscriber')) {
      console.log('subscriber', this.data.get('subscriber'));
      this.subscribe(EVENT_OPENGRAPH_UPDATE, ({ detail: { name, value } }) => {
        console.log('update', name, this.data.get('subscriber'));
        if (name === this.data.get('subscriber')) {
          this.inputTarget.value = value;
        }
      });

      this.subscribe(EVENT_OPENGRAPH_FETCHING, () => {
        this.inputTarget.setAttribute('disabled', true);
      });

      this.subscribe(EVENT_OPENGRAPH_COMPLETE, () => {
        this.inputTarget.removeAttribute('disabled');
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
    this.disableSubscribers();

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
        this.enableSubscribers();
        currentTarget.removeAttribute('disabled');
      });
  }

  disableSubscribers() {
    this.publish(EVENT_OPENGRAPH_FETCHING);
  }

  enableSubscribers() {
    this.publish(EVENT_OPENGRAPH_COMPLETE);
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
