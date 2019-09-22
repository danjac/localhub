export const formElements = formElement => Array.from(formElement.elements);

export const serialize = (elements, multipart) => {
  const data = multipart ? new FormData() : new URLSearchParams();
  elements.forEach(field => {
    if (field.name && !field.disabled) {
      switch (field.type) {
        case 'reset':
        case 'button':
        case 'submit':
          break;
        case 'file':
          if (multipart) {
            data.append(field.name, field.files[0]);
          }
          break;
        case 'radio':
        case 'checkbox':
          if (field.checked) {
            data.append(field.name, field.value);
          }
          break;
        case 'select-multiple':
          Array.from(field.options)
            .filter(option => option.selected)
            .forEach(option => {
              data.append(field.name, option.value);
            });
          break;
        default:
          data.append(field.name, field.value);
      }
    }
  });
  return data;
};
