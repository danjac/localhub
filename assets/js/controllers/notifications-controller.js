// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';
import Cookies from 'js-cookie';

import { Controller } from 'stimulus';

const COOKIE_NAME = 'disable-subscribe-btn';

let registration = null;

export default class extends Controller {
  connect() {
    // check browser can do notifications, and permission OK.
    try {
      this.checkBrowserCompatibility();
      this.registerServiceWorker();
    } catch (e) {
      console.log('Compatibility issue:', e.toString());
    }
  }

  registerServiceWorker() {
    const url = this.data.get('service-worker-url');

    const onRegister = swRegistration => {
      registration = swRegistration;
      return registration.pushManager.getSubscription().then(subscription => {
        if (!subscription) {
          this.show();
        }
      });
    };

    return navigator.serviceWorker.getRegistration(url).then(swRegistration => {
      if (swRegistration) {
        console.log('found service worker');
        return onRegister(swRegistration);
      }
      console.log('registering new service worker');
      return navigator.serviceWorker.register(url).then(onRegister);
    });
  }

  subscribe(event) {
    event.preventDefault();
    const options = {
      applicationServerKey: this.urlB64ToUint8Array(
        this.data.get('vapid-public-key')
      ),
      userVisibleOnly: true
    };
    registration.pushManager.subscribe(options).then(subscription => {
      this.remove();
      return axios.post(
        this.data.get('subscribe-url'),
        JSON.stringify(subscription),
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
    });
  }

  show() {
    this.element.classList.remove('d-hide');
  }

  disable() {
    // remove button
    Cookies.set(COOKIE_NAME, true, {
      domain: this.data.get('domain'),
      expires: 360
    });
    this.remove();
  }

  remove() {
    this.element.remove();
  }

  checkBrowserCompatibility() {
    if (!('serviceWorker' in navigator)) {
      throw new Error('serviceWorker not available');
    }
    if (!('PushManager' in window)) {
      throw new Error('PushManager not available');
    }
    if (!('Notification' in window)) {
      throw new Error('Notification not available');
    }
    if (Notification.permission === 'denied') {
      throw new Error('Permission denied');
    }
    if (Cookies.get(COOKIE_NAME)) {
      throw new Error('Subscribe button disabled by user');
    }
  }

  urlB64ToUint8Array(base64String) {
    const mod = base64String.length % 4;
    const padding = '='.repeat((4 - mod) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; i += 1) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}
