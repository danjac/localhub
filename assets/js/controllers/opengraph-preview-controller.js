// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { Events } from '@utils/constants';
import * as classList from '@utils/class-list';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = [
    'clear',
    'fetch',
    'container',
    'description',
    'descriptionPreview',
    'fullPreview',
    'image',
    'imagePreview',
    'input',
    'listener',
    'titlePreview',
  ];

  connect() {
    this.bus.sub(Events.FORM_FETCHING, () => this.data.set('disabled', true));
    this.bus.sub(Events.FORM_COMPLETE, () => this.data.delete('disabled'));
    this.validate();
  }

  validate(event) {
    let value;
    if (event) {
      event.stopPropagation();
      if (event.type === 'paste' && event.clipboardData) {
        value = event.clipboardData.getData('text/plain');
      } else {
        value = event.currentTarget.value;
      }
    } else {
      value = this.inputTarget.value;
    }
    if (value && this.validateURL() && !this.data.has('disabled')) {
      this.fetchTarget.removeAttribute('disabled');
      return true;
    } else {
      this.fetchTarget.setAttribute('disabled', true);
      return false;
    }
  }

  clear(event) {
    event.preventDefault();
    this.clearPreview();
    this.clearListeners(['image', 'description']);
  }

  fetch(event) {
    event.preventDefault();

    // prevent refetch
    const { currentTarget } = event;

    if (
      !this.validate() ||
      this.data.has('disabled') ||
      currentTarget.getAttribute('disabled')
    ) {
      return false;
    }

    const url = this.inputTarget.value.trim();

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

  clearListeners(targets = ['title', 'description', 'image']) {
    Array.from(this.listenerTargets)
      .filter((target) =>
        targets.includes(target.getAttribute(`data-${this.identifier}-listener-value`))
      )
      .forEach((target) => (target.value = ''));
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
    this.clearTarget.setAttribute('disabled', true);

    this.titlePreviewTarget.innerText = '';

    this.descriptionTargets.forEach((el) => {
      el.innerText = '';
    });

    this.imageTargets.forEach((el) => {
      el.setAttribute('src', '');
    });

    [
      this.containerTarget,
      this.fullPreviewTarget,
      this.descriptionPreviewTarget,
      this.imagePreviewTarget,
      this.titlePreviewTarget,
    ].forEach((el) => this.hideElement(el));
  }

  updatePreview(title, description, image) {
    if (title) {
      this.titlePreviewTarget.innerText = title;
      this.showElement(this.titlePreviewTarget);
    }

    if (description) {
      Array.from(this.descriptionTargets).forEach((el) => (el.innerText = description));
    }

    if (image) {
      Array.from(this.imageTargets).forEach((el) => el.setAttribute('src', image));
    }

    if (description || image || title) {
      this.showElement(this.containerTarget);
      this.clearTarget.removeAttribute('disabled');
    }

    if (description && image) {
      this.showElement(this.fullPreviewTarget);
    } else if (description) {
      this.showElement(this.descriptionPreviewTarget);
    } else if (image) {
      this.showElement(this.imagePreviewTarget);
    }
  }

  getActiveClass(el) {
    return el.getAttribute(`data-${this.identifier}-active-class`);
  }

  getInactiveClass(el) {
    return el.getAttribute(`data-${this.identifier}-inactive-class`) || 'hidden';
  }

  showElement(el) {
    classList.add(el, this.getActiveClass(el));
    classList.remove(el, this.getInactiveClass(el));
  }

  hideElement(el) {
    classList.remove(el, this.getActiveClass(el));
    classList.add(el, this.getInactiveClass(el));
  }

  handleServerError() {
    this.clearListeners();
    this.toaster.error(this.data.get('errorMessage'));
  }

  validateURL() {
    return this.inputTarget.checkValidity();
  }
}
