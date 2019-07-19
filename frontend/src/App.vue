<template>
  <div id="app" class="container">
    <header class="navbar bg-dark px-2 py-1 my-2">
      <section class="navbar-section">
        <a class="navbar-brand mr-2 text-light" href="/">
          Localhub
        </a>
      </section>
      <section class="navbar-section">
        <router-link class="btn btn-link text-light" to="/">Home</router-link>
        <router-link class="btn btn-link text-light" to="/about"
          >About</router-link
        >
      </section>
    </header>

    <router-view />
  </div>
</template>
