// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  /*
  Renders oembed element depending on source e.g. an image, video, audio,
  iframe etc. Ensures the correct CSS class is applied. This is handled
  on page load once the actual element is rendered so we know how to
  apply the correct class.
  */
  connect() {
    if (
      this.element.querySelector('iframe, video, audio') &&
      !this.element.querySelector('script')
    ) {
      this.element.classList.add('video-responsive');
    } else {
      // if we just have embedded images, make these responsive.
      this.element.querySelectorAll('img').forEach(el => {
        el.classList.add('img-responsive');
      });
    }
  }
}
