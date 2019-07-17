// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';
import caretXY from 'caret-xy';

const TAB_KEY = 9;
const RETURN_KEY = 13;
const ARROW_UP = 38;
const ARROW_DOWN = 40;

export default class extends Controller {
  static targets = ['selector', 'input'];

  select(event) {
    event.preventDefault();
    // should be handled from returned HTML
    this.handleSelection(event.currentTarget);
    this.inputTarget.focus();
  }

  keypress(event) {
    if (!this.selectorOpen) {
      return true;
    }

    let firstItem = null;
    let nextItem = null;
    let prevItem = null;

    switch (event.which) {
      case TAB_KEY:
      case RETURN_KEY:
        this.handleSelection(
          this.selectorTarget.querySelector(
            'li.selected > [data-typeahead-value]'
          )
        );
        event.preventDefault();
        return false;
      case ARROW_UP:
        event.preventDefault();
        firstItem = this.selectorTarget.querySelector('li.selected');
        if (firstItem) {
          prevItem = firstItem.previousElementSibling;
          if (prevItem) {
            firstItem.classList.remove('selected');
            prevItem.classList.add('selected');
          }
        }
        return false;
      case ARROW_DOWN:
        event.preventDefault();
        firstItem = this.selectorTarget.querySelector('li.selected');
        if (firstItem) {
          nextItem = firstItem.nextElementSibling;
          if (nextItem) {
            firstItem.classList.remove('selected');
            nextItem.classList.add('selected');
          }
        }
        return false;
      default:
        return true;
    }
  }

  typeahead(event) {
    if (!this.keypress(event)) {
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
    if (!searchUrl) {
      return false;
    }

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
    const { top, left, height } = caretXY(this.inputTarget);
    const rect = this.inputTarget.getBoundingClientRect();
    this.selectorTarget.style.top = rect.top + top + height + 'px';
    this.selectorTarget.style.left = left + 'px';
    this.selectorTarget.classList.remove('d-hide');
  }

  closeSelector() {
    this.selectorTarget.classList.add('d-hide');
    this.removeChildNodes(this.selectorTarget);
  }

  removeChildNodes(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  get selectorOpen() {
    return !this.selectorTarget.classList.contains('d-hide');
  }
}
