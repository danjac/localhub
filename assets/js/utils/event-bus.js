// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

const subscribe = (name, callback) => {
  document.body.addEventListener(name, callback);
  return () => document.body.removeEventListener(name, callback);
};

const publish = (name, data = {}) => {
  const event = new CustomEvent(name, {
    detail: Object.assign({}, data),
  });
  document.body.dispatchEvent(event);
};

export default {
  publish,
  subscribe,
};
