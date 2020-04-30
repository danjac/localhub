// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

export function getViewport() {
  // returns the height and width of the current viewport.
  return {
    height: window.innerHeight || document.documentElement.clientHeight,
    width: window.innerWidth || document.documentElement.clientWidth,
  };
}

export function fadeOut(el, callback) {
  // gradually reduces opacity. Once less than zero,
  // callback is called.
  el.style.opacity = 1;
  (function fade() {
    if ((el.style.opacity -= 0.1) < 0) {
      callback();
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

export function maximizeZIndex(el) {
  // makes the z-index of this element highest in DOM, to ensure it is not overlapped by other
  // elements. Useful for modals, popup menus and tooltips, etc.
  //
  el.style.zIndex = maxZIndex() + 1;
  return el;
}

export function fitIntoViewport(el) {
  const viewport = getViewport();
  const rect = el.getBoundingClientRect();

  return el.style.position === 'absolute'
    ? fitAbsoluteIntoViewport(el, viewport, rect)
    : fitRelativeIntoViewport(el, viewport, rect);
}

const fitAbsoluteIntoViewport = (el, viewport, rect) => {
  if (rect.bottom >= viewport.height) {
    el.style.top = 'auto';
  }

  if (rect.right >= viewport.width) {
    el.style.left = 'auto';
  }
  return el;
};

const fitRelativeIntoViewport = (el, viewport, rect) => {
  if (rect.top < 0) {
    el.style.top = 0;
    el.style.bottom = 'auto';
  } else if (rect.bottom >= viewport.height) {
    el.style.top = 'auto';
    el.style.bottom = 0;
  }
  if (rect.left < 0) {
    el.style.left = 0;
    el.style.right = 'auto';
  } else if (rect.right >= viewport.width) {
    el.style.left = 'auto';
    el.style.right = 0;
  }
  return el;
};
