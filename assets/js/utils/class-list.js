// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

export function add(el, classnames) {
  return new ClassList(el).add(classnames);
}

export function remove(el, classnames) {
  return new ClassList(el).remove(classnames);
}

export function toggle(el, classnames) {
  return new ClassList(el).toggle(classnames);
}

export class ClassList {
  constructor(element) {
    this.element = element;
  }

  splitClassnames(classnames) {
    return classnames.split(/ /);
  }

  add(classnames) {
    this.element.classList.add.apply(
      this.element.classList,
      this.splitClassnames(classnames)
    );
    return this.element;
  }

  remove(classnames) {
    this.element.classList.remove.apply(
      this.element.classList,
      this.splitClassnames(classnames)
    );
    return this.element;
  }

  toggle(classnames) {
    this.element.classList.toggle.apply(
      this.element.classList,
      this.splitClassnames(classnames)
    );
    return this.element;
  }
}
