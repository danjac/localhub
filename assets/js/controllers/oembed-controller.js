// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import * as classList from '@/utils/class-list';
import ApplicationController from '@/controllers/application-controller';

export default class extends ApplicationController {
  /*
  Renders oembed element depending on source e.g. an image, video, audio,
  iframe etc. Ensures the correct CSS class is applied. This is handled
  on page load once the actual element is rendered so we know how to
  apply the correct class. If no such element is embedded then the whole
  element is removed.

  */
  connect() {
    const videoClass = this.data.get('video-class');
    const embedded = this.element.querySelector('iframe, video, audio');

    if (videoClass && embedded && !this.element.querySelector('script')) {
      classList.add(embedded, videoClass);
    } else {
      const images = this.element.querySelectorAll('img');
      const imageClass = this.data.get('image-class');
      if (imageClass && images.length > 0) {
        images.forEach((el) => {
          classList.add(el, imageClass);
        });
      } else {
        this.element.remove();
      }
    }
  }
}
