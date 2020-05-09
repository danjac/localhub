// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import getCaretPosition from 'textarea-caret';

import * as classList from '@utils/class-list';
import { Keys } from '@utils/constants';
import { fitIntoViewport, maximizeZIndex } from '@utils/dom-helpers';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Adds typeahead functionality to form input for handling tag and user mentions.

  actions:
    select: when a specific selection is clicked
    keydown: key trigger to check if a selection character has been entered (# or @)

  data:
    tag-search-url: AJAX endpoint to fetch tag selections. If not included then
      tag selections will not be enabled.
     mention-search-url: AJAX endpoint to fetch mention selections. If not included then
      mention selections will not be enabled.

  targets:
    selector: menu element used to contain HTML returned from endpoints.
    input: <input> or <textarea>
    */
  static targets = ['selector', 'input'];

  connect() {
    document.addEventListener('keydown', (event) => {
      if (event.keyCode === Keys.ESC) {
        this.closeSelector();
      }
    });
    document.addEventListener('click', () => {
      this.closeSelector();
    });

    this.config = JSON.parse(this.data.get('config'));
  }

  select(event) {
    event.preventDefault();
    // should be handled from returned HTML
    this.handleSelection(event.currentTarget);
    this.inputTarget.focus();
  }

  keydown(event) {
    if (
      this.selectorOpen &&
      [Keys.ARR_DOWN, Keys.ARR_UP, Keys.RTN].indexOf(event.which) > -1
    ) {
      event.preventDefault();
    }
  }

  keyup(event) {
    if (!this.handleSelectorEvents(event)) {
      return false;
    }

    let matched = false;

    for (let i = 0; i < this.config.length; ++i) {
      const { url, key } = this.config[i];
      if (this.handleTypeahead(url, key)) {
        matched = true;
        break;
      }
    }

    if (!matched) {
      this.closeSelector();
      return true;
    }

    return false;
  }

  handleSelectorEvents(event) {
    if (!this.selectorOpen) {
      return true;
    }

    let firstItem = null;
    let nextItem = null;
    let prevItem = null;

    switch (event.which) {
      case Keys.TAB:
      case Keys.RTN:
        this.handleSelection(this.selectorTarget.querySelector('li.selected'));
        event.preventDefault();
        return false;
      case Keys.ARR_UP:
        event.preventDefault();
        firstItem = this.selectorTarget.querySelector('li.selected');
        if (firstItem) {
          prevItem = firstItem.previousElementSibling;
          if (prevItem) {
            classList.remove(firstItem, this.selectedClass);
            classList.add(prevItem, this.selectedClass);
          }
        }
        return false;
      case Keys.ARR_DOWN:
        event.preventDefault();
        firstItem = this.selectorTarget.querySelector('li.selected');
        if (firstItem) {
          nextItem = firstItem.nextElementSibling;
          if (nextItem) {
            classList.remove(firstItem, this.selectedClass);
            classList.add(nextItem, this.selectedClass);
          }
        }
        return false;
      default:
        return true;
    }
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
    // only trigger if no other text after this
    const nextChar = value.slice(selectionStart, selectionStart + 1).trim();
    if (nextChar || !text || text.match(/[\s#<>!.?[\]|{}]+/)) {
      return false;
    }

    this.doSearch(text.trim(), searchUrl);
    return true;
  }

  doSearch(text, searchUrl) {
    axios
      .get(searchUrl, {
        params: {
          q: text,
        },
      })
      .then((response) => {
        if (response.data) {
          this.selectorTarget.innerHTML = response.data;
          const results = this.selectorTarget.querySelectorAll(
            '[data-typeahead-value]'
          );
          if (
            results.length &&
            results[0].getAttribute(`data-${this.identifier}-value`) !==
              text.toLowerCase()
          ) {
            this.openSelector();
          } else {
            this.closeSelector();
          }
        }
      })
      .catch(() => {
        this.closeSelector();
      });
  }

  handleSelection(item) {
    const selection = item && item.getAttribute('data-typeahead-value');
    const key = item && item.getAttribute('data-typeahead-key');
    if (selection && key) {
      const { value, selectionStart } = this.inputTarget;
      const index = value.lastIndexOf(key, selectionStart);
      const tokens = value.replace('\t', '').slice(index).split(/ /);
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
        tokens.slice(1).join(' ') +
        ' ';
      this.inputTarget.selectionEnd = index + selection.length + 2;
    }
    this.closeSelector();
  }

  openSelector() {
    const caret = getCaretPosition(this.inputTarget, this.inputTarget.selectionEnd);
    const { offsetTop, offsetLeft, scrollTop, scrollLeft } = this.inputTarget;

    this.selectorTarget.style.position = 'absolute';

    this.selectorTarget.style.top =
      offsetTop - scrollTop + caret.height + caret.top + 'px';
    this.selectorTarget.style.left = offsetLeft - scrollLeft + caret.left + 'px';

    this.selectorTarget.style.right = 'auto';
    this.selectorTarget.style.bottom = 'auto';

    this.selectorTarget.classList.remove('hidden');

    maximizeZIndex(fitIntoViewport(this.selectorTarget));
  }

  closeSelector() {
    this.selectorTarget.classList.add('hidden');
    this.removeChildNodes(this.selectorTarget);
  }

  removeChildNodes(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  get selectorOpen() {
    return !this.selectorTarget.classList.contains('hidden');
  }

  get selectedClass() {
    return this.data.get('selectedClass') + ' selected';
  }
}
