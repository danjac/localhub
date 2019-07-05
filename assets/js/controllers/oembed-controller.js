// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  connect() {
    // if element contains any rich content (iframe, video, audio, img)
    // assign video-responsive class to the element.
    if (this.element.querySelector('iframe, video, audio, img')) {
      this.element.classList.add('video-responsive');
    }
  }
}
