// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  connect() {
    this.socket = null;

    if (!('WebSocket' in window)) {
      console.log('This browser does not support web sockets');
      return;
    }
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const path = `${scheme}://localhost:8000${this.data.get('url')}`;

    this.socket = new WebSocket(path);

    this.socket.onmessage = function(event) {
      const data = JSON.parse(event.data);
      console.log('RECVDATA', data);
      // we grab the message_id from the data, and pull the latest message
      // from get_message_url (or URL is passed in data)
    };

    this.socket.onclose = function(event) {
      console.log('socket closed', event);
    }

    console.log('SOCKET connected', this.socket);
  }

  disconnect() {
    console.log('disconnect');
    this.socket = null;
  }

  // tbd: add a "typing" indicator
  sendMessage(event) {
    if (!this.socket) {
      console.log('no socket initialized');
      return true;
    }
    event.preventDefault();
    const { currentTarget } = event;
    const input = currentTarget.querySelector('textarea');
    const data = { message: input.value };
    console.log('SENDDATA', data);
    this.socket.send(JSON.stringify(data));
    currentTarget.querySelector('textarea').value = '';
    return false;
  }
}
