// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { Events } from '@utils/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = [
    'button',
    'container',
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
    this.bus.sub(Events.FORM_FETCHING, () => this.data.set('disabled', true));
    this.bus.sub(Events.FORM_COMPLETE, () => this.data.delete('disabled'));
  }

  change() {
    if (this.validateURL() && !this.data.has('disabled')) {
      this.buttonTarget.removeAttribute('disabled');
    } else {
      this.buttonTarget.setAttribute('disabled', true);
    }
  }

  fetch(event) {
    event.preventDefault();

    // prevent refetch
    const { currentTarget } = event;

    if (
      !this.validateURL() ||
      this.data.has('disabled') ||
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

    this.bus.pub(Events.FORM_FETCHING);

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
        this.bus.pub(Events.FORM_COMPLETE);
      });
  }

  clearListeners() {
    this.listenerTargets.forEach((target) => (target.value = ''));
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
    this.containerTarget.classList.add('hidden');
    this.titleTarget.innerText = '';
    this.titleTarget.classList.add('hidden');

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
    ].forEach((el) => el.classList.add('hidden'));
  }

  updatePreview(title, description, image) {
    if (title) {
      this.titleTarget.innerText = title;
      this.titleTarget.classList.remove('hidden');
    }

    if (description) {
      Array.from(this.descriptionTargets).forEach((el) => (el.innerText = description));
    }

    if (image) {
      Array.from(this.imageTargets).forEach((el) => el.setAttribute('src', image));
    }

    if (description || image || title) {
      this.containerTarget.classList.remove('hidden');
    }

    if (description && image) {
      this.fullPreviewTarget.classList.remove('hidden');
    } else if (description) {
      this.descriptionPreviewTarget.classList.remove('hidden');
    } else if (image) {
      this.imagePreviewTarget.classList.remove('hidden');
    }
  }

  handleServerError() {
    this.clearListeners();
    this.toaster.error(this.data.get('errorMessage'));
  }

  validateURL() {
    return this.inputTarget.checkValidity();
  }
}
