import { Controller } from 'stimulus';

export default class extends Controller {
  check(event) {
    // check confirmed flag, just run if set
    if (this.data.has('confirmed')) {
      this.data.delete('confirmed');
      return true;
    }
    // stop both underlying "native" event and any other events in chain
    event.preventDefault();
    event.stopImmediatePropagation();

    const header = this.data.get('header');
    const body = this.data.get('body');

    const onConfirm = () => {
      this.data.set('confirmed', true);
      // note: this doesn't work with "native" events, just with
      // stimulus events in the same data-action.
      this.element.dispatchEvent(new Event(event.type));
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
