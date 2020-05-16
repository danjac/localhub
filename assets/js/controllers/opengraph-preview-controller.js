// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { Events } from '@utils/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['clear', 'fetch', 'container', 'subscriber', 'input'];

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
    // clears OG image and description
    event.preventDefault();
    this.clearPreview();
    // we don't want to remove the title, as user may wish to edit
    this.clearSubscribers(['opengraph_image', 'opengraph_description']);
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
        const { html, fields } = response.data;
        this.updateSubscribers(fields);
        this.updatePreview(html);
      })
      .catch(() => this.handleServerError())
      .finally(() => {
        this.bus.pub(Events.FORM_COMPLETE);
      });
  }

  clearSubscribers(names = ['title', 'opengraph_description', 'opengraph_image']) {
    let targets = Array.from(this.subscriberTargets);
    if (names) {
      targets = targets.filter((target) => names.includes(target.getAttribute('name')));
    }
    targets.forEach((target) => (target.value = ''));
  }

  updateSubscribers(data) {
    Object.keys(data).forEach((name) => {
      Array.from(this.subscriberTargets)
        .filter((target) => target.getAttribute('name') === name)
        .forEach((target) => {
          target.value = data[name];
        });
    });
  }

  updatePreview(content) {
    this.clearTarget.removeAttribute('disabled');
    this.containerTarget.innerHTML = content;
  }

  clearPreview() {
    this.clearTarget.setAttribute('disabled', true);
    this.containerTarget.innerHTML = '';
  }

  handleServerError() {
    this.clearSubscribers();
    this.toaster.error(this.data.get('errorMessage'));
  }

  validateURL() {
    return this.inputTarget.checkValidity();
  }
}
