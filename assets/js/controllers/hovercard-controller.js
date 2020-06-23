// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { maximizeZIndex, fitIntoViewport } from '@/utils/dom-helpers';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['container'];

  connect() {
    this.fetched = false;
    this.notFound = false;
    this.source = null;
  }

  show(event) {
    if (this.notFound || this.isTouchDevice) {
      return;
    }

    if (this.fetched) {
      event.preventDefault();
      this.showContainer();
    } else {
      this.source = axios.CancelToken.source();
      axios
        .get(this.data.get('url'), { cancelToken: this.source.token })
        .then((response) => {
          event.preventDefault();
          this.fetched = true;
          if (!this.hasContainerTarget) {
            const div = document.createElement('div');
            div.classList.add('inline-block');
            div.setAttribute('data-target', `${this.identifier}.container`);
            this.element.appendChild(div);
          }
          this.containerTarget.innerHTML = response.data;
          this.showContainer();
        })
        .catch((err) => {
          if (!axios.isCancel(thrown)) {
            this.notFound = true;
          }
        })
        .finally(() => {
          this.source = null;
        });
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

  showContainer() {
    if (this.hasContainerTarget) {
      this.containerTarget.classList.remove('hidden');
      maximizeZIndex(fitIntoViewport(this.containerTarget.children[0]));
    }
  }

  get isTouchDevice() {
    return 'ontouchstart' in document.documentElement;
  }
}
