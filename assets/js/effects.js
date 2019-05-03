export const fadeOut = el => {
  el.style.opacity = 1;
  (function fade() {
    if ((el.style.opacity -= 0.1) < 0) {
      el.remove();
    } else {
      requestAnimationFrame(fade);
    }
  })();
};
