// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

/* eslint-disable */
const webpack = require('webpack');
const path = require('path');
const TerserJSPlugin = require('terser-webpack-plugin');

module.exports = {
  entry: ['./assets/js/main.js', './assets/css/main.css'],
  mode: process.env.NODE_ENV,
  optimization: {
    minimizer: [new TerserJSPlugin({})],
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          'style-loader',
          { loader: 'css-loader', options: { importLoaders: 1 } },
          'postcss-loader',
        ],
      },
      {
        test: /\.(png|svg|jpg|gif)$/,
        use: {
          loader: 'url-loader',
          options: {
            limit: 8192,
          },
        },
      },
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            plugins: ['@babel/plugin-proposal-class-properties'],
          },
        },
      },
    ],
  },
  resolve: {
    alias: {
      '@controllers': path.resolve(__dirname, './assets/js/controllers'),
      '@utils': path.resolve(__dirname, './assets/js/utils'),
    },
  },
  output: {
    path: path.resolve(__dirname, './assets/dist/'),
  },
};
