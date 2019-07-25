<template>
  <div id="app" class="container">
    <header class="navbar bg-dark px-2 py-1 my-2">
      <section class="navbar-section">
        <a class="navbar-brand mr-2 text-light" href="/">
          LocalHub
        </a>
      </section>

      <section class="navbar-section hide-sm">
        <form
          method="GET"
          action="/search/"
          data-controller="form"
          data-action="form#submit"
        >
          <div class="input-group input-inline">
            <input
              class="form-input"
              name="q"
              type="search"
              placeholder="Search"
            />
            <button class="btn bg-gray text-dark input-group-btn">
              Search
            </button>
          </div>
        </form>
      </section>

      <section class="navbar-section">
        <a class="btn btn-link text-light" href="/people/danjac/">
          <figure class="avatar avatar-sm">
            <img
              src="https://communikit.s3.amazonaws.com/media/cache/1c/cd/1ccd95dd491da83dd8424896db2a85ea.jpg"
              alt="Dan Jacob"
              width="100"
              height="100"
            />
          </figure>

          Dan Jacob
        </a>
        <a class="btn btn-link text-light" href="/account/logout/">Logout</a>
      </section>
    </header>
    <router-view />
  </div>
</template>

<style lang="scss">
.conversation-input {
  height: 2rem;
}
</style>
