// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';

const TAB_KEY = 9;

export default class extends Controller {
  static targets = ['selector', 'input'];

  select(event) {
    event.preventDefault();
    // should be handled from returned HTML
    this.handleSelection(event.currentTarget);
    this.inputTarget.focus();
  }

  typeahead(event) {
    if (event.keyCode === TAB_KEY) {
      this.handleSelection(
        this.selectorTarget.querySelector('[data-typeahead-value]')
      );
      event.preventDefault();
      return false;
    }

    if (!this.handleMentions() && !this.handleTags()) {
      this.closeSelector();
      return true;
    }

    return false;
  }

  handleMentions() {
    return this.handleTypeahead(this.data.get('mention-search-url'), '@');
  }

  handleTags() {
    return this.handleTypeahead(this.data.get('tag-search-url'), '#');
  }

  handleTypeahead(searchUrl, key) {
    const { value, selectionStart } = this.inputTarget;
    const index = value.lastIndexOf(key, selectionStart) + 1;

    if (index === 0) {
      return false;
    }

    const text = value.slice(index, selectionStart);
    if (!text || text.match(/[\s#<>!.?[\]|{}]+/)) {
      return false;
    }

    this.doSearch(text, searchUrl);
    return true;
  }

  doSearch(text, searchUrl) {
    axios.get(searchUrl, { params: { q: text } }).then(response => {
      if (response.data) {
        this.selectorTarget.innerHTML = response.data;
        if (
          this.selectorTarget.querySelectorAll('[data-typeahead-value]').length
        ) {
          this.openSelector();
        } else {
          this.closeSelector();
        }
      }
    });
  }

  handleSelection(item) {
    const selection = item && item.getAttribute('data-typeahead-value');
    const key = item && item.getAttribute('data-typeahead-key');
    if (selection && key) {
      const { value, selectionStart } = this.inputTarget;
      const index = value.lastIndexOf(key, selectionStart);
      const tokens = value
        .replace('\t', '')
        .slice(index)
        .split(/ /);
      const [firstToken] = tokens;
      const remainder = firstToken.match(/\n/)
        ? firstToken.slice(firstToken.indexOf('\n'))
        : '';
      this.inputTarget.value =
        value.slice(0, index) +
        key +
        selection +
        remainder +
        ' ' +
        tokens.slice(1).join(' ');
      this.inputTarget.selectionEnd = index + selection.length + 1;
    }
    this.closeSelector();
  }

  openSelector() {
    this.selectorTarget.classList.remove('d-hide');
  }

  closeSelector() {
    this.selectorTarget.classList.add('d-hide');
    while (this.selectorTarget.firstChild) {
      this.selectorTarget.removeChild(this.selectorTarget.firstChild);
    }
  }
}
