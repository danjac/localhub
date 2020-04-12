import { Controller } from 'stimulus';

const TIMEOUT = 3000;

// client-side alerts
export function createAlert(message, level) {
  const tmpl = document.getElementById('alert-template');
  const clone = tmpl.content.cloneNode(true);
  clone.querySelector('div').classList.add(`toast-${level}`);
  clone.querySelector('span').appendChild(document.createTextNode(message));
  document.getElementById('alert-container').appendChild(clone);
}

export default class extends Controller {
  /*
  Used with an alert element that "fades out" after a few seconds
  after page load.

  data:
    remove-after: number of milliseconds (default: 5000)
  */
  connect() {
    const removeAfter = parseInt(this.data.get('remove-after') || TIMEOUT, 10);
    this.timeout = setTimeout(() => {
      this.dismiss();
      clearTimeout(this.timeout);
    }, removeAfter);
  }

  dismiss() {
    this.fadeOut(this.element);
  }

  fadeOut(el) {
    el.style.opacity = 1;
    (function fade() {
      if ((el.style.opacity -= 0.1) < 0) {
        el.remove();
      } else {
        requestAnimationFrame(fade);
      }
    })();
  }
}
