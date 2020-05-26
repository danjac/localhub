<template>
  <header class="bg-indigo-900 text-white">
    <div class="flex items-center justify-between p-2 md:px-5">
      <div class="flex items-center flex-shrink-0 mr-6" v-if="community">
        <button class="lg:hidden mr-3" type="button">
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            focusable="false"
            role="img"
            class="text-white"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M4 6H20M4 12H20M4 18H20"
              stroke="white"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            ></path>
          </svg>
        </button>

        <img
          :src="community.logo"
          class="mr-1 bg-transparent hidden lg:inline-block"
          width="32"
          height="32"
        />

        <router-link
          :to="{ name: 'Home' }"
          class="text-xl tracking-tight text-white hover:text-gray-100"
          >{{ community.name }}</router-link
        >
      </div>

      <div class="hidden lg:block" v-if="currentUser && community">
        <form method="GET" action="/search/">
          <input
            type="search"
            placeholder="Search..."
            name="q"
            class="appearance-none border border-gray-500 w-full p-1 text-gray-900"
          />
        </form>
      </div>

      <div v-if="currentUser">
        <img
          :src="currentUser.avatar"
          :alt="currentUser.full_name"
          class="rounded-full bg-transparent inline-block mr-1"
          width="32"
          height="32"
        />

        <a href="#" class="inline-block text-white hover:text-gray-100 md:mr-2">
          {{ currentUser.username }}
        </a>
        <a
          href="#"
          @click.prevent="logout"
          class="hidden md:inline-block text-white hover:text-gray-100"
          >Logout
        </a>
      </div>

      <div v-else>
        <router-link
          :to="{ name: 'Login' }"
          class="inline-block text-white hover:text-gray-100 mr-2"
        >
          Login
        </router-link>

        <a href="#" class="inline-block text-white hover:text-gray-100">
          Signup
        </a>
      </div>
    </div>

    <div class="px-2 md:px-5 pb-2 lg:hidden">
      <form
        method="GET"
        action="/search/"
        data-controller="form"
        data-action="form#submit"
      >
        <input
          type="search"
          placeholder="Search..."
          name="q"
          class="appearance-none border border-gray-500 w-full p-1 text-gray-900"
        />
      </form>
    </div>
  </header>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HeaderNav',
  computed: {
    currentUser() {
      return this.$store.state.user;
    },
    community() {
      return this.$store.state.community;
    },
  },
  methods: {
    async logout() {
      await axios.post('/auth/logout/');
      window.location.href = '/';
    },
  },
};
</script>
