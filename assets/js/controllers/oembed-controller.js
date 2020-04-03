// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  /*
  Renders oembed element depending on source e.g. an image, video, audio,
  iframe etc. Ensures the correct CSS class is applied. This is handled
  on page load once the actual element is rendered so we know how to
  apply the correct class. If no such element is embedded then the whole
  element is removed.

  */
  connect() {
    if (
      this.element.querySelector('iframe, video, audio') &&
      !this.element.querySelector('script')
    ) {
      this.element.classList.add('video-responsive');
    } else {
      // if we just have embedded images, make these responsive.
      const images = this.element.querySelectorAll('img');
      if (images.length > 0) {
        images.forEach(el => {
          el.classList.add('img-responsive');
        });
      } else {
        this.element.remove();
      }
    }
  }
}
