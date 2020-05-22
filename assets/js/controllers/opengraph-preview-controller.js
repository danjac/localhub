// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { Events } from '@/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  // fetches preview HTML and fields from server, updates fields and inserts HTML.
  static targets = ['clearButton', 'fetchButton', 'container', 'field', 'input'];

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
    if (value && this.inputTarget.checkValidity() && !this.data.has('disabled')) {
      this.fetchButtonTarget.removeAttribute('disabled');
      return true;
    } else {
      this.fetchButtonTarget.setAttribute('disabled', true);
      return false;
    }
  }

  clear(event) {
    // clears OG image and description
    event.preventDefault();
    this.containerTarget.innerHTML = '';
    // we don't want to remove the title, as user may wish to edit
    this.resetForm(['opengraph_image', 'opengraph_description']);
  }

  fetch(event) {
    event.preventDefault();

    this.containerTarget.innerHTML = '';
    this.clearButtonTarget.setAttribute('disabled', true);

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
      return false;
    }

    this.bus.pub(Events.FORM_FETCHING);

    axios
      .get(this.data.get('preview-url'), { params: { url } })
      .then((response) => {
        const { html, fields } = response.data;
        this.syncForm(fields);
        this.containerTarget.innerHTML = html;
        this.clearButtonTarget.removeAttribute('disabled');
      })
      .catch(() => {
        this.resetForm();
        this.toaster.error(this.data.get('errorMessage'));
      })
      .finally(() => {
        this.bus.pub(Events.FORM_COMPLETE);
      });
  }

  resetForm(names = ['title', 'opengraph_description', 'opengraph_image']) {
    let targets = Array.from(this.fieldTargets);
    if (names) {
      targets = targets.filter((target) => names.includes(target.getAttribute('name')));
    }
    targets.forEach((target) => (target.value = ''));
  }

  syncForm(data) {
    Object.keys(data).forEach((name) => {
      Array.from(this.fieldTargets)
        .filter((target) => target.getAttribute('name') === name)
        .forEach((target) => {
          target.value = data[name];
        });
    });
  }
}
