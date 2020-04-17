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
  static targets = ['image', 'input'];

  change(event) {
    if (event.target.files) {
      this.handleFile(event.target.files[0]);
    }
  }

  drop(event) {
    event.preventDefault();
    event.stopPropagation();
    if (event.dataTransfer && event.dataTransfer.files) {
      this.handleFile(event.dataTransfer.files[0]);
      this.inputTarget.files = event.dataTransfer.files;
    }
  }

  handleFile(file) {
    if (this.isImage(file.name)) {
      this.imageTarget.src = URL.createObjectURL(file);
      this.imageTarget.classList.remove('d-none');
    } else {
      this.imageTarget.classList.add('d-none');
    }
  }

  isImage(url) {
    return url.match(/\.(jpeg|jpg|gif|png)$/) != null;
  }
}
