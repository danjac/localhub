// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { getJSON } from '~/utils/fetch-json';
import { Events } from '~/constants';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  // fetches preview HTML and fields from server, updates fields and inserts HTML.
  static targets = ['clearButton', 'fetchButton', 'container', 'field', 'input'];
  static values = { disabled: Boolean, url: String, errorMessage: String };

  connect() {
    this.bus.sub(Events.FORM_FETCHING, () => (this.disabledValue = true));
    this.bus.sub(Events.FORM_COMPLETE, () => (this.disabledValue = false));
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
    if (value && this.inputTarget.checkValidity() && !this.disabledValue) {
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

  async fetch(event) {
    event.preventDefault();

    this.containerTarget.innerHTML = '';
    this.clearButtonTarget.setAttribute('disabled', true);

    // prevent refetch
    const { currentTarget } = event;

    if (
      !this.validate() ||
      this.disabledValue ||
      currentTarget.getAttribute('disabled')
    ) {
      return false;
    }

    const url = this.inputTarget.value.trim();

    if (!url) {
      return false;
    }

    this.bus.pub(Events.FORM_FETCHING);

    try {
      const response = await getJSON(this.urlValue, { url });
      const { html, fields } = await response.json();
      this.syncForm(fields);
      this.containerTarget.innerHTML = html;
      this.clearButtonTarget.removeAttribute('disabled');
    } catch (err) {
      console.log(err);
      this.resetForm();
      if (this.hasErrorMessageValue) {
        this.toaster.error(this.errorMessageValue);
      }
    } finally {
      this.bus.pub(Events.FORM_COMPLETE);
    }
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
