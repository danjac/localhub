// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

import { HTMLElementEvent } from '../types';

export default class extends Controller {
  static targets = ['textarea'];

  textareaTarget: HTMLInputElement;

  select(event: HTMLElementEvent) {
    const target = event.currentTarget;

    event.preventDefault();

    const { dataset } = target;
    const { markdown } = dataset;
    const [markdownStart, markdownEnd] = markdown.split(/\[SELECTION\]/);

    const { selectionStart, selectionEnd, value } = this.textareaTarget;

    const selectedText = value.substring(selectionStart, selectionEnd);

    const markdownText =
      'multiline' in dataset
        ? selectedText
            .split('\n')
            .map(item => markdownStart + item + markdownEnd)
            .join('\n')
        : markdownStart + selectedText + markdownEnd;

    this.textareaTarget.value =
      value.substring(0, selectionStart) +
      markdownText +
      value.substring(selectionEnd, value.length);
    this.textareaTarget.dispatchEvent(new Event('input'));
  }
}
