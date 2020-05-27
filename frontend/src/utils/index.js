export function getViewport() {
  // returns the height and width of the current viewport.
  return {
    height: window.innerHeight || document.documentElement.clientHeight,
    width: window.innerWidth || document.documentElement.clientWidth,
  };
}

export function fitIntoViewport(el) {
  console.log('fit element into viewport', el);
  const viewport = getViewport();
  const rect = el.getBoundingClientRect();

  if (rect.top < 0) {
    el.style.top = 0;
    el.style.bottom = 'auto';
  } else if (rect.bottom >= viewport.height) {
    el.style.top = el.offsetTop - rect.height + 'px';
    el.style.bottom = 'auto';
  }
  if (rect.left < 0) {
    el.style.left = 0;
    el.style.right = 'auto';
  } else if (rect.right >= viewport.width) {
    el.style.right = 0;
    el.style.left = 'auto';
  }
  return el;
}
