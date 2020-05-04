// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { Events } from '@utils/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = [
    'description',
    'descriptionPreview',
    'fullPreview',
    'image',
    'imagePreview',
    'input',
    'listener',
    'title',
  ];
  connect() {
    this.bus.sub(Events.AJAX_FETCHING, () => this.data.set('fetching', true));
    this.bus.sub(Events.AJAX_COMPLETE, () => this.data.delete('fetching'));
  }

  fetch(event) {
    event.preventDefault();

    // prevent refetch
    const { currentTarget } = event;

    if (
      !this.inputTarget.checkValidity() ||
      this.data.has('fetching') ||
      currentTarget.getAttribute('disabled')
    ) {
      return false;
    }

    const url = this.inputTarget.value;

    if (!url) {
      this.clearPreview();
      return false;
    }

    this.clearPreview();

    currentTarget.setAttribute('disabled', true);
    this.bus.pub(Events.AJAX_FETCHING);

    axios
      .get(this.data.get('preview-url'), { params: { url } })
      .then((response) => {
        const { title, description, image, url } = response.data;

        if (url) {
          this.inputTarget.value = url;
        }

        this.updatePreview(title, description, image);
        this.updateListeners({ title, image, description });
      })
      .catch(() => this.handleServerError())
      .finally(() => {
        this.bus.pub(Events.AJAX_COMPLETE);
        currentTarget.removeAttribute('disabled');
      });
  }

  clearListeners() {
    Array.from(this.listenerTargets).forEach((target) => (target.value = ''));
  }

  updateListeners(data) {
    Object.keys(data).forEach((name) => {
      Array.from(this.listenerTargets)
        .filter(
          (target) =>
            target.getAttribute(`data-${this.identifier}-listener-value`) === name
        )
        .forEach((target) => {
          target.value = data[name];
        });
    });
  }

  clearPreview() {
    this.titleTarget.innerText = '';
    this.titleTarget.classList.add('d-none');

    this.descriptionTargets.forEach((el) => {
      el.innerText = '';
    });

    this.imageTargets.forEach((el) => {
      el.setAttribute('src', '');
    });

    [
      this.fullPreviewTarget,
      this.descriptionPreviewTarget,
      this.imagePreviewTarget,
      this.titleTarget,
    ].forEach((el) => el.classList.add('d-none'));
  }

  updatePreview(title, description, image) {
    if (title) {
      this.titleTarget.innerText = title;
      this.titleTarget.classList.remove('d-none');
    }

    if (description) {
      Array.from(this.descriptionTargets).forEach((el) => (el.innerText = description));
    }

    if (image) {
      Array.from(this.imageTargets).forEach((el) => el.setAttribute('src', image));
    }

    if (description && image) {
      this.fullPreviewTarget.classList.remove('d-none');
    } else if (description) {
      this.descriptionPreviewTarget.classList.remove('d-none');
    } else if (image) {
      this.imagePreviewTarget.classList.remove('d-none');
    }
  }

  handleServerError() {
    this.clearListeners();
    this.toaster.error(this.data.get('errorMessage'));
  }
}
