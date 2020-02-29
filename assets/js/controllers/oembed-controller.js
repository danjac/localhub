// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

export default class extends Controller {
  connect() {
    // if element contains any rich content (iframe, video, audio)
    // assign video-responsive class to the element.
    // ignore if there's a <script> tag as we don't want to break loading
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