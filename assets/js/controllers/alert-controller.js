import { Controller } from 'stimulus';

export default class extends Controller {
  /*
  Used with an alert element that "fades out" after a few seconds
  after page load.

  data:
    remove-after: number of milliseconds (default: 5000)
  */
  connect() {
    const removeAfter = parseInt(this.data.get('remove-after') || 5000, 10);
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
