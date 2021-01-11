const doFetch = (url, method, headers, options) => {
  return fetch(url, {
    method,
    credentials: 'same-origin',
    headers: {
      ...headers,
      'Content-Type': 'application/json',
    },
    ...(options || {}),
  });
};

export const getJSON = (url, params, options) =>
  doFetch(url + (params ? '?' + new URLSearchParams(params) : ''), 'GET', options);

export const postJSON = (url, csrfToken, body, options) =>
  doFetch(
    url,
    'POST',
    { 'X-CSRFToken': csrfToken },
    { ...options, body: JSON.stringify(body || {}) }
  );
