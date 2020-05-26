// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Markdown shortcut selector for highlighting and inserting
  markdown syntax.

  actions:
    select: when markdown syntax selection applied.

  targets:
    textarea: <textarea> element to apply markdown syntax
  */
  static targets = ['textarea', 'previewTab'];

  connect() {
    this.togglePreviewTab();
  }

  togglePreviewTab() {
    if (this.textareaTarget.value.trim()) {
      this.previewTabTarget.removeAttribute('disabled');
    } else {
      this.previewTabTarget.setAttribute('disabled', true);
    }
  }

  select(event) {
    event.preventDefault();

    const { dataset } = event.currentTarget;
    const { markdown } = dataset;
    const [markdownStart, markdownEnd] = markdown.split(/\[SELECTION\]/);

    const { selectionStart, selectionEnd, value } = this.textareaTarget;

    const selectedText = value.substring(selectionStart, selectionEnd);

    const markdownText =
      'multiline' in dataset
        ? selectedText
            .split('\n')
            .map((item) => markdownStart + item + markdownEnd)
            .join('\n')
        : markdownStart + selectedText + (markdownEnd || '');

    this.textareaTarget.value =
      value.substring(0, selectionStart) +
      markdownText +
      value.substring(selectionEnd, value.length);
    ['change', 'keyup', 'keydown', 'input'].forEach((event) =>
      this.textareaTarget.dispatchEvent(new Event(event))
    );
  }
}
