// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { maximizeZIndex, fitIntoViewport } from '@/utils/dom-helpers';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = ['container'];

  show(event) {
    if (!this.containerTarget) {
      return;
    }
    event.stopPropagation();

    if (this.containerTarget.innerHTML) {
      this.showContainer();
    } else {
      axios
        .get(this.data.get('url'))
        .then((response) => {
          this.containerTarget.innerHTML = response.data;
          this.showContainer();
        })
        .catch(() => {
          this.containerTarget.remove();
        });
    }
  }

  hide() {
    if (this.containerTarget) {
      this.containerTarget.classList.add('hidden');
    }
  }

  showContainer() {
    this.containerTarget.classList.remove('hidden');
    maximizeZIndex(fitIntoViewport(this.containerTarget.children[0]));
  }

  disconnect() {
    if (this.containerTarget) {
      this.containerTarget.innerHTML = '';
    }
  }
}
