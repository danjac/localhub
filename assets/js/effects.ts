export function fadeOut(el: HTMLElement) {
  el.style.opacity = '1';
  (function fade() {
    const opacity = parseInt(el.style.opacity, 10) - 0.1;
    if (opacity < 0) {
      el.remove();
    } else {
      requestAnimationFrame(fade);
    }
  })();
}
