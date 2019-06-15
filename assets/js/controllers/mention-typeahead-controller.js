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
    if (event.keyCode === TAB_KEY) {
      this.handleSelection(
        this.selectorTarget.querySelector('[data-mention-typeahead-value]')
      );
      event.preventDefault();
      return false;
    }

    const { value, selectionStart } = this.inputTarget;
    const index = value.lastIndexOf('@', selectionStart) + 1;

    if (index === 0) {
      this.closeSelector();
      return true;
    }

    const text = value.slice(index, selectionStart);
    if (!text || text.match(/[\s#<>!.?[\]|{}]+/)) {
      this.closeSelector();
      return true;
    }

    this.doSearch(text);
    return false;
  }

  doSearch(text) {
    const searchUrl = this.data.get('search-url');

    axios.get(searchUrl, { params: { q: text } }).then(response => {
      if (response.data) {
        this.selectorTarget.innerHTML = response.data;
        if (
          this.selectorTarget.querySelectorAll('[data-mention-typeahead-value]')
            .length
        ) {
          this.openSelector();
        } else {
          this.closeSelector();
        }
      }
    });
  }

  handleSelection(item) {
    const mention = item && item.getAttribute('data-mention-typeahead-value');
    if (mention) {
      const { value, selectionStart } = this.inputTarget;
      const index = value.lastIndexOf('@', selectionStart);
      const tokens = value
        .replace('\t', '')
        .slice(index)
        .split(/ /);
      const [firstToken] = tokens;
      const remainer = firstToken.match(/\n/)
        ? firstToken.slice(firstToken.indexOf('\n'))
        : '';
      this.inputTarget.value =
        value.slice(0, index) +
        '@' +
        mention +
        remainer +
        ' ' +
        tokens.slice(1).join(' ');
      this.inputTarget.selectionEnd = index + mention.length + 1;
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
