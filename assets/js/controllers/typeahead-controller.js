// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import getCaretPosition from 'textarea-caret';

import {
  KEY_ARR_DOWN,
  KEY_ARR_UP,
  KEY_ESC,
  KEY_RTN,
  KEY_TAB,
} from '@utils/application-constants';

import { getViewport, maximizeZIndex } from '@utils/dom-helpers';

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
      if (event.keyCode === KEY_ESC) {
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
      [KEY_ARR_DOWN, KEY_ARR_UP, KEY_RTN].indexOf(event.which) > -1
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
      case KEY_TAB:
      case KEY_RTN:
        this.handleSelection(
          this.selectorTarget.querySelector('li.selected > [data-typeahead-value]')
        );
        event.preventDefault();
        return false;
      case KEY_ARR_UP:
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
      case KEY_ARR_DOWN:
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
    axios
      .get(searchUrl, {
        params: {
          q: text,
        },
      })
      .then((response) => {
        if (response.data) {
          this.selectorTarget.innerHTML = response.data;
          if (this.selectorTarget.querySelectorAll('[data-typeahead-value]').length) {
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
    const { top, left, height } = getCaretPosition(
      this.inputTarget,
      this.inputTarget.selectionEnd
    );
    const { offsetTop, offsetLeft, scrollTop, scrollLeft } = this.inputTarget;

    this.selectorTarget.style.position = 'absolute';
    this.selectorTarget.style.top = offsetTop - scrollTop + height + top + 'px';
    this.selectorTarget.style.left = offsetLeft - scrollLeft + left + 'px';
    this.selectorTarget.classList.remove('d-none');

    const viewport = getViewport();
    const rect = this.selectorTarget.getBoundingClientRect();

    if (rect.bottom > viewport.height) {
      let selectorTop = rect.bottom - viewport.height;
      if (selectorTop + rect.height < viewport.height) {
        selectorTop = viewport.height - rect.height;
      }
      this.selectorTarget.style.top = selectorTop + 'px';
      this.selectorTarget.style.bottom = 'auto';
    }

    if (
      rect.width + rect.left > viewport.width ||
      rect.width + rect.right > viewport.width
    ) {
      this.selectorTarget.style.left = '25%';
    }
    maximizeZIndex(this.selectorTarget);
  }

  closeSelector() {
    this.selectorTarget.classList.add('d-none');
    this.removeChildNodes(this.selectorTarget);
  }

  removeChildNodes(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  get selectorOpen() {
    return !this.selectorTarget.classList.contains('d-none');
  }
}
