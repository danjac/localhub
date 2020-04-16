// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  /*
  Markdown shortcut selector for highlighting and inserting
  markdown syntax.

  actions:
    select: when markdown syntax selection applied.

  targets:
    textarea: <textarea> element to apply markdown syntax
  */
  static targets = ['textarea'];

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
    this.textareaTarget.dispatchEvent(new Event('input'));
  }
}
