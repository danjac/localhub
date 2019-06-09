import { Controller } from 'stimulus';
import axios from 'axios';

const TAB_KEY = 9;

export default class extends Controller {
  static targets = ['selector', 'input'];

  select(event) {
    event.preventDefault();
    this.handleSelection(event.currentTarget);
    this.inputTarget.focus();
  }

  typeahead(event) {
    // tbd: check for tab, if selection pick first result
    if (event.keyCode === TAB_KEY) {
      this.handleSelection(this.selectorTarget.querySelector('li.menu-item a'));
      return;
    }
    const { value } = this.inputTarget;
    const index = value.lastIndexOf('@');
    const text = value.slice(index + 1, value.length);

    if (!text || text.indexOf(' ') > -1) {
      this.closeSelector();
      return;
    }

    const searchUrl = this.data.get('search-url');

    axios.get(searchUrl, { params: { q: text } }).then(response => {
      if (response.data) {
        this.selectorTarget.innerHTML = response.data;
        if (this.selectorTarget.querySelectorAll('li.menu-item').length) {
          this.openSelector();
        } else {
          this.closeSelector();
        }
      }
    });
  }

  handleSelection(item) {
    const value = item.getAttribute('data-mention-typeahead-value');
    if (value) {
      const index = this.inputTarget.value.lastIndexOf('@');
      this.inputTarget.value =
        this.inputTarget.value.slice(0, index + 1) + value + ' ';
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
