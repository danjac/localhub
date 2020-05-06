// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

export default class extends ApplicationController {
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
      this.element.classList.add.apply(
        this.element.classList,
        this.get('video-class').split(/ /)
      );
    } else {
      // if we just have embedded images, make these responsive.
      const images = this.element.querySelectorAll('img');
      if (images.length > 0) {
        images.forEach((el) => {
          el.classList.add.apply(el.classList, this.data.get('image-class').split(/ /));
        });
      } else {
        this.element.remove();
      }
    }
  }
}
