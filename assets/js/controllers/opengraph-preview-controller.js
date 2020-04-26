// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { TOAST_ERROR } from '@utils/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['image', 'description', 'title', 'progress'];

  change(event) {
    const { currentTarget } = event;

    this.titleTarget.classList.add('d-none');
    this.imageTarget.classList.add('d-none');
    this.descriptionTarget.classList.add('d-none');

    this.titleTarget.innerText = '';
    this.descriptionTarget.innerText = '';
    this.imageTarget.setAttribute('src', '');

    const url = event.currentTarget.value;

    if (!url) {
      return;
    }

    currentTarget.setAttribute('disabled', true);

    // this.progressTarget.classList.toggle('d-none');

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
        }
        if (image) {
          this.imageTarget.setAttribute('src', image);
          this.imageTarget.classList.remove('d-none');
        }
      })
      .catch((err) => this.handleServerError(err))
      .finally(() => {
        console.log('restore.....');
        currentTarget.removeAttribute('disabled');
        // this.progressTarget.classList.toggle('d-none');
      });
  }

  handleServerError(err) {
    if (err.response) {
      const { status, statusText } = err.response;
      this.toast(TOAST_ERROR, `${status}: ${statusText}`);
    }
  }
}
