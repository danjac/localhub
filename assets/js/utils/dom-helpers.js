// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

export function getViewport() {
  // returns the height and width of the current viewport.
  return {
    height: window.innerHeight || document.documentElement.clientHeight,
    width: window.innerWidth || document.documentElement.clientWidth,
  };
}

export function fadeOut(el) {
  // gradually reduces opacity, then removes element.
  el.style.opacity = 1;
  (function fade() {
    if ((el.style.opacity -= 0.1) < 0) {
      el.remove();
    } else {
      requestAnimationFrame(fade);
    }
  })();
}

export function maxZIndex() {
  // returns highest z-index on the page
  // https://stackoverflow.com/questions/1118198/how-can-you-figure-out-the-highest-z-index-in-your-document
  return (
    Array.from(document.querySelectorAll('body *'))
      .map((el) => parseFloat(getComputedStyle(el).zIndex))
      .filter((index) => !isNaN(index))
      .sort()
      .pop() || 0
  );
}
