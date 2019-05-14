import { Controller } from 'stimulus';

export default class extends Controller {
  check(event) {
    // check confirmed flag, just run if set
    if (this.data.has('confirmed')) {
      this.data.delete('confirmed');
      return true;
    }
    // stop both "native" event and any other events in chain
    event.preventDefault();
    event.stopImmediatePropagation();

    const header = this.data.get('header');
    const body = this.data.get('body');

    const onConfirm = () => {
      this.data.set('confirmed', true);
      switch (event.type) {
        case 'click':
          this.element.click();
          break;
        case 'submit':
          this.element.submit();
          break;
        case 'reset':
          this.element.reset();
          break;
        default:
          this.element.dispatchEvent(new Event(event.type));
      }
    };

    const dialog = this.application.getControllerForElementAndIdentifier(
      document.getElementById('confirm-dialog'),
      'confirm-dialog'
    );

    dialog.open({
      body,
      header,
      onConfirm
    });

    return false;
  }
}
