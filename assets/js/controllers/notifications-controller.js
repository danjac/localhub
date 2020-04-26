// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import { urlB64ToUint8Array } from '@utils/encoders';
import ApplicationController from './application-controller';

let registration = null;

export default class extends ApplicationController {
  /*
  Manages browser notifications using a serviceWorker. If the browser or device does
  not support browser notifications (e.g. depending on security settings) then
  the subscription button is removed.

  actions:
    subscribe: subscribes browser to service
    unsubscribe: unsubscribes browser from service

  data:
    service-worker-url: URL pointing to the serviceWorker.
    subscribe-url: URL to AJAX endpoint subscribing this browser.
    unsubscribe-url: URL to AJAX endpoint unsubscribing this browser.
    vapid-public-key: the Vapid service public subscription key

  targets:
    subscribeBtn: button or other element to subscribe to notifications
    unsubscribeBtn: button or other element to unsubscribe from notifications
  */
  static targets = ['subscribeBtn', 'unsubscribeBtn'];

  connect() {
    // check browser can do notifications, and permission OK.
    try {
      this.checkBrowserCompatibility();
      this.registerServiceWorker();
    } catch (e) {
      this.element.remove();
      console.log('Compatibility issue:', e.toString());
    }
  }

  registerServiceWorker() {
    const url = this.data.get('service-worker-url');

    const onRegister = (swRegistration) => {
      registration = swRegistration;
      return registration.pushManager.getSubscription().then((subscription) => {
        if (subscription) {
          this.showUnsubscribeBtn();
        } else {
          this.showSubscribeBtn();
        }
      });
    };

    return navigator.serviceWorker.getRegistration(url).then((swRegistration) => {
      if (swRegistration) {
        console.log('found existing service worker');
        return onRegister(swRegistration);
      }
      console.log('registering new service worker');
      return navigator.serviceWorker.register(url).then(onRegister);
    });
  }

  subscribe(event) {
    event.preventDefault();
    const options = {
      applicationServerKey: urlB64ToUint8Array(this.data.get('vapid-public-key')),
      userVisibleOnly: true,
    };
    registration.pushManager.subscribe(options).then((subscription) => {
      this.showUnsubscribeBtn();
      return this.syncWithServer(subscription, this.data.get('subscribe-url'));
    });
  }

  unsubscribe(event) {
    event.preventDefault();
    this.showSubscribeBtn();
    registration.pushManager
      .getSubscription()
      .then((subscription) =>
        subscription
          .unsubscribe()
          .then(this.syncWithServer(subscription, this.data.get('unsubscribe-url')))
      );
  }

  syncWithServer(subscription, url) {
    return axios.post(url, JSON.stringify(subscription), {
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  showSubscribeBtn() {
    this.element.classList.remove('d-none');
    this.subscribeBtnTarget.classList.remove('d-none');
    this.unsubscribeBtnTarget.classList.add('d-none');
  }

  showUnsubscribeBtn() {
    this.element.classList.remove('d-none');
    this.unsubscribeBtnTarget.classList.remove('d-none');
    this.subscribeBtnTarget.classList.add('d-none');
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
  }
}
