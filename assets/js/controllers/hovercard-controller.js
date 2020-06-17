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
    if (this.containerTarget.innerHTML) {
      this.containerTarget.classList.remove('hidden');
    } else {
      axios
        .get(this.data.get('url'))
        .then((response) => {
          event.stopPropagation();
          this.containerTarget.innerHTML = response.data;
          maximizeZIndex(fitIntoViewport(this.containerTarget.children[0]));
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

  disconnect() {
    if (this.containerTarget) {
      this.containerTarget.innerHTML = '';
    }
  }
}
