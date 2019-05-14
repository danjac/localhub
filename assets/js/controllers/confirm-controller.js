import { Controller } from 'stimulus';

export default class extends Controller {
  // use with an action 'chain' e.g. data-action="confirm#check ajax#delete"
  check(event) {
    return this.confirm(event, () =>
      this.element.dispatchEvent(new Event(event.type))
    );
  }

  // "native" events: just fire native click, submit etc
  // e.g. data-action="confirm#submit"
  click(event) {
    return this.confirm(event, () => this.element.click());
  }

  submit(event) {
    return this.confirm(event, () => this.element.submit());
  }

  reset(event) {
    return this.confirm(event, () => this.element.reset());
  }

  confirm(event, handler) {
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
      handler();
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
