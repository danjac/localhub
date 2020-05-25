<template>
  <div id="app">
    <header class="bg-indigo-900 text-white">
      <div class="flex items-center justify-between p-2 md:px-5">
        <div class="flex items-center flex-shrink-0 mr-6">
          <button class="lg:hidden mr-3" data-action="sidebar#toggle" type="button">
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
            src="https://d1hfgy95btx02f.cloudfront.net/media/cache/4f/e3/4fe33ebb6cfe647946d267f42a04e1ab.png"
            class="mr-1 bg-transparent hidden lg:inline-block"
            width="32"
            height="32"
          />

          <a href="/" class="text-xl tracking-tight text-white hover:text-gray-100"
            >Kotiseutu</a
          >
        </div>

        <div class="hidden lg:block">
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

        <div>
          <img
            src="https://d1hfgy95btx02f.cloudfront.net/media/cache/9d/36/9d366cd50fdd52864be3dcd85039676c.png"
            alt="Dan Jacob"
            class="rounded-full bg-transparent inline-block mr-1"
            width="32"
            height="32"
          />

          <a
            href="/people/danjac/"
            class="inline-block text-white hover:text-gray-100 md:mr-2"
          >
            danjac
          </a>
          <a
            href="/account/logout/"
            class="hidden md:inline-block text-white hover:text-gray-100"
            data-turbolinks="false"
            data-controller="ajax"
            data-action="ajax#post"
            data-ajax-redirect="/"
            >Logout</a
          >
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
    <div class="mt-2 px-2 md:px-5 flex min-h-full">
      <router-view />
    </div>
  </div>
</template>

<style></style>
