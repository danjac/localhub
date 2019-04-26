export const csrfSafeMethod = method =>
  /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);

export const getCookie = name => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie
      .split(';')
      .map(cookie => cookie.trim())
      .forEach(cookie => {
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.split('=')[1]);
        }
      });
  }
  return cookieValue;
};
