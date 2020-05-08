// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

/* eslint-disable */
module.exports = {
  purge: {
    content: ['./templates/**/*.html'],
    options: {
      whitelist: [
        'bg-gray-600',
        'bg-blue-600',
        'bg-green-600',
        'bg-orange-600',
        'bg-red-600',
      ],
    },
  },
  theme: {
    extend: {},
  },
  variants: {},
  plugins: [],
};
