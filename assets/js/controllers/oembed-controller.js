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
    const videoClasses = this.data.get('video-class').split(/ /);
    const embedded = this.element.querySelector('iframe, video, audio');

    if (videoClasses && embedded && !this.element.querySelector('script')) {
      embedded.classList.add.apply(embedded.classList, videoClasses);
    } else {
      // if we just have embedded images, make these responsive.
      const images = this.element.querySelectorAll('img');
      const imageClasses = this.data.get('image-class').split(/ /);
      if (imageClasses && images.length > 0) {
        images.forEach((el) => {
          el.classList.add.apply(el.classList, imageClasses);
        });
      } else {
        this.element.remove();
      }
    }
  }
}
