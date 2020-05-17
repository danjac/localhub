// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from '@/controllers/application-controller';

export default class extends ApplicationController {
  /*
  Shows preview of image. Use with an <input> file widget.

  actions:
    change:
        when image file is selected.

  targets:
      image: the <img> element holding the image.
  */
  static targets = ['image', 'input', 'fileSize'];

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
      this.imageTarget.classList.remove('hidden');
    } else {
      this.imageTarget.classList.add('hidden');
    }
    if (this.hasFileSizeTarget) {
      const size = this.readableFileSize(file.size);
      if (size) {
        this.fileSizeTarget.innerText = size;
        this.fileSizeTarget.classList.remove('hidden');
      } else {
        this.fileSizeTarget.classList.add('hidden');
      }
    }
  }

  isImage(url) {
    return url.match(/\.(jpeg|jpg|gif|png)$/) != null;
  }

  readableFileSize(bytes) {
    const units = ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const thresh = 1000;
    const under = (bytes) => Math.abs(bytes) < thresh;

    if (under(bytes)) {
      return bytes + ' bytes';
    }
    for (let i = -1; i < units.length; ++i) {
      if (under(bytes)) {
        console.log(i, bytes);
        return bytes.toFixed(1) + ' ' + units[i];
      }
      bytes /= thresh;
    }
  }
}
