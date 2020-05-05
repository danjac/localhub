// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

/* eslint-disable */
module.exports = {
  purge: ['./src/**/*.html'],
  plugins: [require('tailwindcss')('./tailwind.config.js'), require('autoprefixer')],
};
