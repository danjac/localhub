// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  targets = ['container'];

  show() {
    if (this.containerTarget.innerHTML) {
      this.containerTarget.classList.remove('hidden');
    } else {
      axios.get(this.data.url).then((response) => {
        this.containerTarget.innerHTML = response.data;
      });
    }
  }

  hide() {
    this.containerTarget.classList.add('hidden');
  }

  disconnect() {
    this.containerTarget.innerHTML = '';
  }
}
