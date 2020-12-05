// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { isTouchDevice, maximizeZIndex, fitIntoViewport } from '~/utils/dom-helpers';
import ApplicationController from './application-controller';

// cached URL results - if we have more than one card on a page with identical URL,
// then fetch the same result from here instead of making another round-trip to the server.
const cache = {};

export default class extends ApplicationController {
  static targets = ['container'];
  static values = { url: String, objectUrl: String };

  connect() {
    this.source = null;
    this.isTouchDevice = isTouchDevice();
  }

  async show(event) {
    const cacheKey = this.hasObjectUrlValue
      ? this.urlValue + '|' + this.objectUrlValue
      : this.urlValue;

    let html = cache[cacheKey];

    if (html === null || this.isTouchDevice) {
      return;
    }

    if (html) {
      event.preventDefault();
      this.render(html);
      return;
    }

    this.source = axios.CancelToken.source();

    const params = {};

    if (this.hasObjectUrl) {
      params['object_url'] = this.objectUrlValue;
    }

    try {
      const response = await axios.get(this.urlValue, {
        cancelToken: this.source.token,
        params,
      });
      event.preventDefault();
      cache[cacheKey] = html = response.data;
      this.render(html);
    } catch (err) {
      if (!axios.isCancel(err)) {
        cache[cacheKey] = null;
      }
    } finally {
      this.source = null;
    }
  }

  hide() {
    if (this.hasContainerTarget) {
      this.containerTarget.classList.add('hidden');
    }
    if (this.source) {
      this.source.cancel();
    }
  }

  render(html) {
    if (!this.hasContainerTarget) {
      const div = document.createElement('div');
      div.classList.add('inline-block');
      div.setAttribute(`data-${this.identifier}-target`, 'container');
      this.element.appendChild(div);
    }
    this.containerTarget.innerHTML = html;
    this.containerTarget.classList.remove('hidden');
    maximizeZIndex(fitIntoViewport(this.containerTarget.children[0]));
  }
}
