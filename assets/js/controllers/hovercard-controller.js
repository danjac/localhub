// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { isTouchDevice, maximizeZIndex, fitIntoViewport } from '@/utils/dom-helpers';
import ApplicationController from './application-controller';

// cached URL results - if we have more than one card on a page with identical URL,
// then fetch the same result from here instead of making another round-trip to the server.
const cache = {};

export default class extends ApplicationController {
  static targets = ['container'];

  connect() {
    this.source = null;
    this.isTouchDevice = isTouchDevice();
  }

  show(event) {
    const url = this.data.get('url');

    let html = cache[url];

    if (html === null || this.isTouchDevice) {
      return;
    }

    if (html) {
      event.preventDefault();
      this.showContainer(html);
      return;
    }

    this.source = axios.CancelToken.source();

    axios
      .get(url, { cancelToken: this.source.token })
      .then((response) => {
        event.preventDefault();
        if (!this.hasContainerTarget) {
          const div = document.createElement('div');
          div.classList.add('inline-block');
          div.setAttribute('data-target', `${this.identifier}.container`);
          this.element.appendChild(div);
        }
        this.containerTarget.innerHTML = response.data;
        cache[url] = html = response.data;
        this.showContainer(html);
      })
      .catch((err) => {
        if (!axios.isCancel(err)) {
          cache[url] = null;
        }
      })
      .finally(() => {
        this.source = null;
      });
  }

  hide() {
    if (this.hasContainerTarget) {
      this.containerTarget.classList.add('hidden');
    }
    if (this.source) {
      this.source.cancel();
    }
  }

  showContainer(html) {
    if (!this.hasContainerTarget) {
      const div = document.createElement('div');
      div.classList.add('inline-block');
      div.setAttribute('data-target', `${this.identifier}.container`);
      this.element.appendChild(div);
    }
    this.containerTarget.innerHTML = html;
    this.containerTarget.classList.remove('hidden');
    maximizeZIndex(fitIntoViewport(this.containerTarget.children[0]));
  }
}
