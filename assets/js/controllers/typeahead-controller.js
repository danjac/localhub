// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';
import axios from 'axios';
import getCaretPosition from 'textarea-caret';

import getViewport from '@utils/getViewport';
import maxZIndex from '@utils/maxZIndex';

const ESC_KEY = 27;
const TAB_KEY = 9;
const RETURN_KEY = 13;
const ARROW_UP = 38;
const ARROW_DOWN = 40;

export default class extends Controller {
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
      if (event.keyCode === ESC_KEY) {
        this.closeSelector();
      }
    });
    document.addEventListener('click', () => {
      this.closeSelector();
    });

    this.urls = JSON.parse(this.data.get('urls'));
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
      [ARROW_DOWN, ARROW_UP, RETURN_KEY].indexOf(event.which) > -1
    ) {
      event.preventDefault();
    }
  }

  keyup(event) {
    if (!this.handleSelectorEvents(event)) {
      return false;
    }

    let matched = false;

    for (let i = 0; i < this.urls.length; ++i) {
      const { url, key } = this.urls[i];
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
      case TAB_KEY:
      case RETURN_KEY:
        this.handleSelection(
          this.selectorTarget.querySelector('li.selected > [data-typeahead-value]')
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

    if (rect.height + rect.bottom > viewport.height) {
      this.selectorTarget.style.top = viewport.height + 'px';
    }

    if (
      rect.width + rect.left > viewport.width ||
      rect.width + rect.right > viewport.width
    ) {
      this.selectorTarget.style.left = '25%';
    }
    this.selectorTarget.zIndex = maxZIndex() + 1;
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
