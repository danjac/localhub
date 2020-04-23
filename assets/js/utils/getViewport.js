// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

export default function () {
  // returns the height and width of the current viewport.
  return {
    height:window.innerHeight || document.documentElement.clientHeight,
    width:window.innerWidth || document.documentElement.clientWidth
  }
}
