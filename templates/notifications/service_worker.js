self.addEventListener('push', function(event) {
  const payload = event.data
    ? event.data.text()
    : {
        body: 'No Content',
        head: 'No Content',
        icon: ''
      };
  const data = JSON.parse(payload);
  const { head, body, icon } = data;
  const url = data.url || self.location.origin;
  event.waitUntil(
    self.registration.showNotification(head, {
      body,
      data: { url },
      icon
    })
  );
});

self.addEventListener('notificationclick', function(event) {
  event.preventDefault();
  event.notification.close();
  const { url } = event.notification.data;
  event.waitUntil(
    self.clients
      .matchAll({
        includeUncontrolled: true,
        type: 'window'
      })
      .then(clientList => {
        if (clientList.length > 0) {
          const [client] = clientList;
          if (client.url === url && 'focus' in client) {
            return client.focus();
          }
        }
        return self.clients.openWindow(url);
      })
  );
});
