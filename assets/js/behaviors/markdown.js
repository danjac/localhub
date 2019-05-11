import onmount from 'onmount';

onmount('[data-markdown-shortcut]', function() {
  this.addEventListener('click', event => {
    event.preventDefault();
    const { target } = event;
    const textarea = target.parentNode.parentNode.querySelector(
      'textarea.markdownx-editor'
    );
    const { selectionStart, selectionEnd } = textarea;
    const { markdownShortcut } = target.dataset;
    const [markdownStart, markdownEnd] = markdownShortcut.split(
      /\[SELECTION\]/
    );
    const selectedText = textarea.value.substring(selectionStart, selectionEnd);
    const markdownText = markdownStart + selectedText + markdownEnd;
    textarea.value =
      textarea.value.substring(0, selectionStart) +
      markdownText +
      textarea.value.substring(selectionEnd, textarea.value.length);
    // trigger insert event so we update preview
    // doesn't appear to work immediately
    textarea.dispatchEvent(new CustomEvent('markdownx.update'));
  });
});
