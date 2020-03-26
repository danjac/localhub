import {
  Controller
} from 'stimulus';

export default class extends Controller {
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
