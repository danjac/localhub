import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['textarea'];

  select(event) {
    event.preventDefault();

    const { markdown } = event.currentTarget.dataset;
    const [markdownStart, markdownEnd] = markdown.split(/\[SELECTION\]/);

    const { selectionStart, selectionEnd, value } = this.textareaTarget;

    const selectedText = value.substring(selectionStart, selectionEnd);
    const markdownText = markdownStart + selectedText + markdownEnd;

    this.textareaTarget.value =
      value.substring(0, selectionStart) +
      markdownText +
      value.substring(selectionEnd, value.length);
    this.textareaTarget.dispatchEvent(new Event('input'));
  }
}
