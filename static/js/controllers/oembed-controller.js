// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import * as classList from '~/utils/class-list';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Renders oembed element depending on source e.g. an image, video, audio,
  iframe etc. Ensures the correct CSS class is applied. This is handled
  on page load once the actual element is rendered so we know how to
  apply the correct class. If no such element is embedded then the whole
  element is removed.

  */
  static classes = ['video', 'image'];

  connect() {
    const embedded = this.element.querySelector('iframe, video, audio');

    if (this.hasVideoClass && embedded && !this.element.querySelector('script')) {
      classList.add(embedded, this.videoClass);
    } else {
      const images = this.element.querySelectorAll('img');
      if (this.hasImageClass && images.length > 0) {
        images.forEach((el) => {
          classList.add(el, this.imageClass);
        });
      } else {
        this.element.remove();
      }
    }
  }
}
