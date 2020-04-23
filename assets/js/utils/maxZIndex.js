// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

export default function () {
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
