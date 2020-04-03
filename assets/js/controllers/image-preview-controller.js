// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  /*
  Shows preview of image. Use with an <input> file widget.

  actions:
    change:
        when image file is selected.

  targets:
      image: the <img> element holding the image.
  */
  static targets = ['image'];

  change(event) {
    if (event.target.files) {
      const file = event.target.files[0];
      if (this.isImage(file.name)) {
        this.imageTarget.src = URL.createObjectURL(file);
        this.imageTarget.classList.remove('d-hide');
      } else {
        this.imageTarget.classList.add('d-hide');
      }
    }
  }

  isImage(url) {
    return url.match(/\.(jpeg|jpg|gif|png)$/) != null;
  }
}
